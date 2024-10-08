from django.urls import path
from .views import pago, crear_reserva

urlpatterns = [
    path('pago/', pago, name='pago'),
    path('crear-reserva/', crear_reserva, name='crear_reserva'),  # URL para la vista de crear reserva
]