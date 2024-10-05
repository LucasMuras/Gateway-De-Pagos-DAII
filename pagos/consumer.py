import pika
import json

def callback(ch, method, properties, body):
    # Procesar el evento de reserva que se recibe
    print(f" [x] Evento recibido: {body.decode()}")
    reserva_event = json.loads(body)
    procesar_pago(reserva_event)

def procesar_pago(reserva_event):
    print(f" [x] Procesando pago para reserva: {reserva_event['reserva_id']}, monto: {reserva_event['amount']}")
    # Aquí implementarías la lógica para realizar el pago
    # Después de procesar el pago, podrías publicar un evento de confirmación de pago

#Gateway de pagos se suscribe a los topicos que contienen eventos de interes
def suscribir_a_reservas():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar el Exchange de tipo 'topic'
    channel.exchange_declare(exchange='reservas_exchange', exchange_type='topic')

    # Declarar la cola para gateway de pagos
    channel.queue_declare(queue='gateway_pagos')

    # Enlazar la cola al exchange con la clave de enrutamiento para eventos de reservas nuevas
    channel.queue_bind(exchange='reservas_exchange', queue='gateway_pagos', routing_key='reservas.nueva') #reservas.nueva es un evento dentro del topico reservas

    print(" [*] Esperando eventos de reservas...")

    # Consumir los mensajes desde la cola de gateway_pagos
    channel.basic_consume(queue='gateway_pagos', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

if __name__ == '__main__':
    suscribir_a_reservas()
