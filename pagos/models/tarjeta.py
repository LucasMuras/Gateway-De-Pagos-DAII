from django.db import models

class Tarjeta(models.Model):
    TIPO_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard')
    ]

    nombre_titular = models.CharField(max_length=255)
    numero = models.CharField(max_length=16)
    fecha_expiracion = models.DateField()
    cvv = models.CharField(max_length=3)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f'{self.nombre} - {self.tipo}'