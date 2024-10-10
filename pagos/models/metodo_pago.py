from django.db import models
from .pagador import Pagador
from .tarjeta import Tarjeta

# Create your models here.
class MetodoPago(models.Model):
    OPCIONES_CUOTAS = [
        (3, '3 Cuotas'),
        (6, '6 Cuotas'),
        (12, '12 Cuotas'),
    ]
    
    en_cuotas = models.BooleanField(default=False)
    tipo = models.CharField(max_length=20, default="Tarjeta") #unica opción de la versión "tarjeta"
    cuotas = models.IntegerField(choices=OPCIONES_CUOTAS, null=True, blank=True)
    tarjeta = models.ForeignKey('Tarjeta', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.tipo}'