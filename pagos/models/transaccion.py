from django.db import models
from .metodo_pago import MetodoPago
from .pagador import Pagador

# Create your models here.
class Transaccion(models.Model):
    ESTADO_CHOICES = [
        #('iniciado', 'Iniciado'),
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('fallida', 'Fallida'),
    ]

    pagador = models.ForeignKey(Pagador, on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    descripcion = models.TextField(null=True, blank=True)
    destinatario = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Transacción #{self.id} - {self.usuario.username} - {self.monto}'