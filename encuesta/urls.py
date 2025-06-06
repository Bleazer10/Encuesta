from django.contrib import admin
from django.urls import path
from evaluacion import views
from evaluacion.views import ver_respuestas
from evaluacion.views import menu_principal
from evaluacion.views import login_profesor, logout_profesor

urlpatterns = [
    path('', menu_principal, name='menu'),
    path('acceso/', views.validar_cedula, name='validar_cedula'),
    path('admin/', admin.site.urls),
    path('encuesta/', views.encuesta_view, name='encuesta'),
    path('gracias/', views.gracias, name='gracias'),
    path('respuestas/', ver_respuestas, name='ver_respuestas'),
    path('login-profesor/', login_profesor, name='login_profesor'),
    path('logout-profesor/', logout_profesor, name='logout_profesor'),
    path('estadisticas/', views.estadisticas_respuestas, name='estadisticas_respuestas'),
    path('menu_profesor/', views.menu_profesor, name='menu_profesor'),
]
