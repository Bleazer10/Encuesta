from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import RespuestaAnonima, CedulaUsada
from .preguntas import PREGUNTAS
from .models import Profesor

def logout_profesor(request):
    request.session.flush()  # Elimina toda la sesión
    return redirect('menu')  # Redirige al menú principal


def menu_principal(request):
    return render(request, 'menu.html')

# Usado para prevenir múltiples respuestas durante una ejecución
cedulas_respondidas = set()

# Cargar lista de cédulas autorizadas
with open('cedulas_autorizadas.txt') as f:
    cedulas_autorizadas = set(line.strip() for line in f)


def validar_cedula(request):
    error = False
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        ya_respondio = CedulaUsada.objects.filter(cedula=cedula).exists()

        if cedula in cedulas_autorizadas and not ya_respondio:
            request.session['autorizado'] = True
            request.session['cedula'] = cedula  # Guardamos la cédula para marcar después
            return redirect('encuesta')
        else:
            error = True

    return render(request, 'validar_cedula.html', {'error': error})

def encuesta_view(request):
    if not request.session.get('autorizado'):
        return redirect('validar_cedula')

    if request.method == 'POST':
        respuestas = [request.POST.get(f'q{i}') for i in range(1, len(PREGUNTAS)+1)]
        if all(respuestas):
            RespuestaAnonima.objects.create(
                fecha=now(),
                respuestas=respuestas
            )
            # Marcar cédula como usada
            CedulaUsada.objects.get_or_create(cedula=request.session.get('cedula'))
            request.session.flush()
            return redirect('gracias')
        else:
            return render(request, 'encuesta.html', {
                'preguntas': PREGUNTAS,
                'error': 'Debes responder todas las preguntas.'
            })

    return render(request, 'encuesta.html', {
        'preguntas': PREGUNTAS
    })

from django.core.paginator import Paginator

def ver_respuestas(request):
    if not request.session.get('profesor_autenticado'):
        return redirect('login_profesor')

    todas_respuestas = RespuestaAnonima.objects.all().order_by('-fecha')


    paginator = Paginator(todas_respuestas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ver_respuestas.html', {
        'respuestas': page_obj,     
        'page_obj': page_obj,       
        'preguntas': PREGUNTAS
    })


def gracias(request):
    return render(request, 'gracias.html')

def login_profesor(request):
    if request.session.get('profesor_autenticado'):
        return redirect('menu_profesor')
     
    error = False
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        try:
            prof = Profesor.objects.get(username=username)
            if prof.check_password(password):
                request.session['profesor_autenticado'] = True
                return redirect('menu_profesor')
        except Profesor.DoesNotExist:
            pass
        error = True
    return render(request, 'login_profesor.html', {'error': error})

def menu_profesor(request):
    if not request.session.get('profesor_autenticado'):
        return redirect('login_profesor')
    return render(request, 'menu_profesor.html')


def estadisticas_respuestas(request):
    respuestas = RespuestaAnonima.objects.all()
    total_estudiantes = respuestas.count()
    puntos = {'A': 3, 'B': 2, 'C': 1}

    if total_estudiantes == 0:
        preguntas_con_categoria = list(zip(PREGUNTAS, ['Sin datos'] * len(PREGUNTAS)))
        conclusion = "Sin datos suficientes"
    else:
        suma_por_pregunta = [0] * len(PREGUNTAS)
        for r in respuestas:
            for idx, valor in enumerate(r.respuestas):
                suma_por_pregunta[idx] += puntos.get(valor, 0)

        promedios_numericos = [s / total_estudiantes for s in suma_por_pregunta]

        def clasificar_promedio(p):
            if p >= 2.5:
                return 'A - Bueno'
            elif p >= 1.8:
                return 'B - Regular'
            else:
                return 'C - Deficiente'

        preguntas_con_categoria = list(zip(PREGUNTAS, [clasificar_promedio(p) for p in promedios_numericos]))

        promedio_general = sum(promedios_numericos) / len(promedios_numericos)
        conclusion = clasificar_promedio(promedio_general)

    return render(request, 'estadisticas.html', {
        'respuestas_totales': total_estudiantes,
        'promedios': preguntas_con_categoria,
        'conclusion': conclusion
    })
