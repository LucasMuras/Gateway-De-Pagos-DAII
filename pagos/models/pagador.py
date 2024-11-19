from django.db import models

# Create your models here.
class Pagador(models.Model):
    id_external = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default="hola")
    surname = models.CharField(max_length=100, default="hola")
    phone = models.IntegerField(default=0)
    document = models.IntegerField(default=0)
    birth_date = models.DateField(default="2000-01-01")
    email = models.EmailField()

    def __str__(self):
        return f'{self.name} {self.surname}'