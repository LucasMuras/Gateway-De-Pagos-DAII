from django.db import models
from .metodo_pago import MetodoPago
from .pagador import Pagador

# Create your models here.
class Transaccion(models.Model):
    ESTADO_CHOICES = [
        ('iniciado', 'Iniciado'),
        ('valido', 'Valido'),
        ('fallido', 'Fallido'),
        ('pendiente', 'Pendiente'),
    ]

    pagador = models.ForeignKey(Pagador, on_delete=models.CASCADE)
    destinatario = models.CharField(max_length=255, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(null=True, blank=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    es_reembolso = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Transacción #{self.id} - {self.pagador.nombre} - {self.monto}'