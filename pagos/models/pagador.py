from django.db import models

# Create your models here.
class Pagador(models.Model):
    id_externa = models.IntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.IntegerField()
    email = models.EmailField()

    def __str__(self):
        return f'{self.nombre} {self.apellido}'