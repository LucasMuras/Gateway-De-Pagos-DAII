# pagos/productor.py
import json
import pika  # Asegúrate de tener la biblioteca pika instalada

def enviar_reserva(pagador, destinatario, monto):
    # Crear la conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar el intercambio (exchange) y la cola (queue)
    channel.exchange_declare(exchange='reserva', exchange_type='topic')

    # Crear el mensaje
    reserva_data = {
        'pagador': {
            'id_externa': pagador.id_externa,
            'nombre': pagador.nombre,
            'apellido': pagador.apellido,
            'dni': pagador.dni,
            'email': pagador.email,
        },
        'destinatario': {
            'id_externa': destinatario.id_externa,
            'nombre': destinatario.nombre,
            'email': destinatario.email,
        },
        'monto': monto,
    }

    # Enviar el mensaje
    channel.basic_publish(
        exchange='reserva',
        routing_key='reservaIniciada',
        body=json.dumps(reserva_data)
    )

    # Cerrar la conexión
    connection.close()
