from django.db import models

# Create your models here.
class Destinatario(models.Model):
    id_external = models.IntegerField(default=0)
    hotel = models.IntegerField(default=0)
    floor = models.IntegerField(default=0)
    name = models.CharField(max_length=50, default="hola")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    state = models.CharField(max_length=50, default="hola")
    double_beds_amount = models.IntegerField(default=0)  # Default value set to 0
    single_beds_amount = models.IntegerField(default=0)  # Default value set to 0
    images = models.CharField(max_length=250, default="default_image.jpg")
    email = models.EmailField()

    def __str__(self):
        return f'{self.name}'