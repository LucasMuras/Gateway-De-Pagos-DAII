from django.db import models
from .pagador import Pagador
from .destinatario import Destinatario

# Create your models here.
class Reembolso(models.Model):
    ESTADO_CHOICES = [
        ('valido', 'Valido'),
        ('pendiente', 'Pendiente'),
    ]

    id_external = models.IntegerField(default=0)
    room = models.IntegerField(default=0)
    start_date = models.DateField(default="2000-01-01")
    end_date = models.DateField(default="2000-01-01")
    client = models.IntegerField(default=0)
    services = models.CharField(max_length=250, default="hola")
    pagador = models.ForeignKey(Pagador, on_delete=models.CASCADE)
    destinatario = models.ForeignKey(Destinatario, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    def __str__(self):
        return f'Reembolso - {self.pagador.name} - {self.monto}'