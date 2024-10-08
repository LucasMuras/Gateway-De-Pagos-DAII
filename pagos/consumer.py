# pagos/consumer.py
import json
import pika


from django.shortcuts import render

from urllib.parse import quote
from django.shortcuts import redirect
from django.urls import reverse
import os
import django
# Configura el entorno de Django para que el script pueda usar sus modelos y configuraciones
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway_de_pagos.settings')  # Reemplaza con el nombre de tu proyecto
django.setup()
# Suponiendo que tienes estos modelos
from .models import Pagador, Destinatario

from django.shortcuts import render
from django.http import HttpRequest
from .models import Pagador, Destinatario  # Asegúrate de que la ruta sea correcta
from .forms import PagoForm  # Asegúrate de que la ruta sea correcta
import json
def callback(ch, method, properties, body):
    reserva_data = json.loads(body)

    # Crear y guardar los objetos Pagador y Destinatario
    pagador = Pagador.objects.create(
        nombre=reserva_data['pagador']['nombre'],
        apellido=reserva_data['pagador']['apellido'],
        email=reserva_data['pagador']['email'],
        telefono=reserva_data['pagador']['telefono']
    )

    destinatario = Destinatario.objects.create(
        nombre=reserva_data['destinatario']['nombre']
    )

    # Imprimir los detalles por consola
    print("Reserva recibida:")
    print(f"Pagador: {pagador.nombre} {pagador.apellido}")
    print(f"Email: {pagador.email}")
    print(f"Teléfono: {pagador.telefono}")
    print(f"Destinatario: {destinatario.nombre}")

    # No se redirige en este caso, ya que estamos en el contexto de un consumidor


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar el intercambio (exchange) y la cola (queue)
    channel.exchange_declare(exchange='reservas', exchange_type='topic')
    channel.queue_declare(queue='reserva_queue')

    # Vincular la cola al intercambio
    channel.queue_bind(exchange='reservas', queue='reserva_queue', routing_key='reserva.iniciada')

    # Establecer el consumidor
    channel.basic_consume(queue='reserva_queue', on_message_callback=callback, auto_ack=True)

    print("Esperando reservas. Presiona CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    main()
