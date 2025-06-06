from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class RespuestaAnonima(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    respuestas = models.JSONField()

    def __str__(self):
        return f"Respuesta del {self.fecha.strftime('%Y-%m-%d %H:%M:%S')}"

class CedulaUsada(models.Model):
    cedula = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.cedula

class Profesor(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # guardamos el hash

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username