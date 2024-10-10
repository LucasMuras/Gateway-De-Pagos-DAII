import pika
from .services.procesamiento_transaccion import guardar_entidades

# funcion que se encarga de conectar a RabbitMQ a los tópicos reserva y backoffice (para hacer la simulacion)
def conectar_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='reserva', exchange_type='topic')
    channel.exchange_declare(exchange='backoffice', exchange_type='topic')
    return connection, channel


# función que se encarga de escuchar los eventos de reservas que se guardaron en nuestra cola reserva_queue
def callback_reserva(ch, method, properties, body):
    mensaje = body.decode()

    # Vamos validando que llegan ciertos eventos que nos interesan del tópico de reserva
    if method.routing_key == 'reservaIniciada':
        print(f"Reserva iniciada: {mensaje}")
        guardar_entidades(mensaje)
    elif method.routing_key == 'reservaCancelada':
        print(f"Reserva cancelada: {mensaje}")
    else:
        print(f"Evento no manejado: {mensaje}")

# función que se encarga de escuchar los eventos de backoffice que se guardaron en nuestra cola backoffice_queue
def callback_backoffice(ch, method, properties, body):
    mensaje = body.decode()
    print(mensaje)


    # Vamos validando que llegan ciertos eventos que nos interesan del tópico de backoffice
    if method.routing_key == 'reservaCancelada':
        print(f"Reserva cancelada: {mensaje}")
    else:
        print(f"Evento no manejado: {mensaje}")


# función que se encarga de escuchar los tópicos de reserva y backoffice
def escuchar_topicos():
    connection, channel = conectar_rabbitmq()

    #RESERVA
    # Declaramos la cola de reserva y la vinculamos al tópico de reserva
    # Es decir: todo lo que venga de reserva, se "almacena" en la cola de reserva qeu creamos
    # Solo se almacerarán los eventos que tengan la clave según "routing_key"
    channel.queue_declare(queue='reserva_queue')
    channel.queue_bind(exchange='reserva', queue='reserva_queue', routing_key='reservaIniciada')
    channel.queue_bind(exchange='reserva', queue='reserva_queue', routing_key='reservaCancelada')

    # Nos suscribimos a nuestra cola de reserva y manejamos los eventos/mensajes que lleguen con el callback_reserva
    channel.basic_consume(queue='reserva_queue', on_message_callback=callback_reserva, auto_ack=True)


    #BACKOFFICE
    # Declaramos la cola de backoffice y la vinculamos al tópico de backoffice
    # Es decir: todo lo que venga de backoffice, se "almacena" en la cola de backoffice que creamos
    # Solo se almacerarán los eventos que tengan la clave según "routing_key"
    channel.queue_declare(queue='backoffice_queue')
    channel.queue_bind(exchange='backoffice', queue='backoffice_queue', routing_key='reservaCancelada')

    # Nos suscribimos a nuestra cola de backoffice y manejamos los eventos/mensajes que lleguen con el callback_backoffice
    channel.basic_consume(queue='backoffice_queue', on_message_callback=callback_backoffice, auto_ack=True)


    print('Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()


# para ejecutar este módulo, se debe ejecutar el siguiente comando en la terminal: python -m pagos.rabbitmq
if __name__ == '__main__':
    escuchar_topicos()