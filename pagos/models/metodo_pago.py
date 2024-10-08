from django.db import models
from .pagador import Pagador
from .tarjeta import Tarjeta

# Create your models here.
class MetodoPago(models.Model):
    TIPO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('mercadoPago', 'MercadoPago'),
        ('transferencia', 'Transferencia Bancaria'),
    ]

    usuario = models.ForeignKey(Pagador, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES) #unica opción de la versión "tarjeta"
    tarjeta = models.ForeignKey('Tarjeta', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.tipo}'