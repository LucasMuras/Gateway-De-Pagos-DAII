# pagos/productor.py
import json
import pika  # Asegúrate de tener la biblioteca pika instalada

def enviar_reserva(pagador, destinatario, monto):
    # Crear la conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar el intercambio (exchange) y la cola (queue)
    channel.exchange_declare(exchange='reservas', exchange_type='topic')

    # Crear el mensaje
    reserva_data = {
        'pagador': {
            'nombre': pagador.nombre,
            'apellido': pagador.apellido,
            'email': pagador.email,
            'telefono': pagador.telefono,
        },
        'destinatario': {
            'nombre': destinatario.nombre,
        },
        'monto': monto,
    }

    # Enviar el mensaje
    channel.basic_publish(
        exchange='reservas',
        routing_key='reserva.iniciada',
        body=json.dumps(reserva_data)
    )

    # Cerrar la conexión
    connection.close()
