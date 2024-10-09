from django.db import models

# Create your models here.
class Destinatario(models.Model):
    id_externa = models.IntegerField()
    nombre = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f'{self.nombre}'