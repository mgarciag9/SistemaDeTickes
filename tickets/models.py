from django.db import models
from django.utils import timezone
from tickets.utils import valida_cedula

class Ticket(models.Model):
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.IntegerField()
    dni = models.CharField(max_length=10, validators=[valida_cedula])
    descripcion = models.TextField()
    creado_en = models.DateTimeField(default=timezone.now)
    atendido_en = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.nombre} {self.apellidos} - {self.dni}'
