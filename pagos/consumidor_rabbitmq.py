import pika, json
from .services.procesamiento_transaccion import guardar_entidades, iniciar_reembolso


# funcion que se encarga de conectar a RabbitMQ a los tópicos reserva y backoffice (para hacer la simulacion)
def conectar_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='reserva', exchange_type='topic')
    channel.exchange_declare(exchange='backoffice', exchange_type='topic')
    return connection, channel


def enviar_mensaje_a_rabbitmq(message, exchange, routing_key):
    message = json.dumps(message)
    #print('toy en rabbit', message)
    connection, channel = conectar_rabbitmq()
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
    #print(f" [x] Sent '{message}'")
    connection.close()


def recibir_mensajes_sns(event):
    #print('AEAEAEEAEAEAEAEEAEAEAE')
    if 'Message' in event:
        sns_message = json.loads(event['Message'])
        sns_topic = event.get('TopicArn', '')
        sns_event_type = event.get('Subject', '')
        print("hola", sns_event_type)

        if 'reserva' in sns_topic:
            print('akdkjadhAAAAAAAAHHHHHHHHHHH')
            enviar_mensaje_a_rabbitmq(sns_message, 'reserva', sns_event_type)
        elif 'backoffice' in sns_topic:
            enviar_mensaje_a_rabbitmq(sns_message, 'backoffice', sns_event_type)
    else:
        print("El evento SNS no contiene un campo 'Message'")



# función que se encarga de escuchar los eventos de reservas que se guardaron en nuestra cola reserva_queue
def callback_reserva(ch, method, properties, body):
    mensaje = body.decode()

    try:
        if method.routing_key == 'reservaIniciada':
            print(f"Reserva iniciada: {mensaje}")
            guardar_entidades(mensaje, 'transaccion')
            #No inicio porque eso se hace en el pago (endpoint)
        elif method.routing_key == 'reservaCancelada':
            print(f"Reserva cancelada: {mensaje}")
            reembolso = guardar_entidades(mensaje, 'reembolso')
            iniciar_reembolso(reembolso)

        else:
            print(f"Evento no manejado: {mensaje}")
        
        # Confirma el mensaje solo si se procesó correctamente
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        # Puedes optar por no enviar el ack aquí para que RabbitMQ reintente el mensaje
        # Si deseas manejar el error sin reintentos, puedes hacer basic_nack
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Reencola el mensaje si lo deseas


# función que se encarga de escuchar los eventos de backoffice que se guardaron en nuestra cola backoffice_queue
def callback_backoffice(ch, method, properties, body):
    mensaje = body.decode()
    print(mensaje)
    ch.basic_ack(delivery_tag=method.delivery_tag)


    # Vamos validando que llegan ciertos eventos que nos interesan del tópico de backoffice
    if method.routing_key == 'reservaCancelada':
        print(f"Reserva cancelada: {mensaje}")
    else:
        print(f"Evento no manejado: {mensaje}")


# función que se encarga de escuchar los tópicos de reserva y backoffice
def escuchar_topicos():
    connection, channel = conectar_rabbitmq()
    #print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')

    #RESERVA
    # Declaramos la cola de reserva y la vinculamos al tópico de reserva
    # Es decir: todo lo que venga de reserva, se "almacena" en la cola de reserva qeu creamos
    # Solo se almacerarán los eventos que tengan la clave según "routing_key"
    channel.queue_declare(queue='reserva_queue')
    channel.queue_bind(exchange='reserva', queue='reserva_queue', routing_key='reservaIniciada')
    channel.queue_bind(exchange='reserva', queue='reserva_queue', routing_key='reservaCancelada')

    # Nos suscribimos a nuestra cola de reserva y manejamos los eventos/mensajes que lleguen con el callback_reserva
    channel.basic_consume(queue='reserva_queue', on_message_callback=callback_reserva, auto_ack=False)


    #BACKOFFICE
    # Declaramos la cola de backoffice y la vinculamos al tópico de backoffice
    # Es decir: todo lo que venga de backoffice, se "almacena" en la cola de backoffice que creamos
    # Solo se almacerarán los eventos que tengan la clave según "routing_key"
    channel.queue_declare(queue='backoffice_queue')
    channel.queue_bind(exchange='backoffice', queue='backoffice_queue', routing_key='reservaCancelada')

    # Nos suscribimos a nuestra cola de backoffice y manejamos los eventos/mensajes que lleguen con el callback_backoffice
    channel.basic_consume(queue='backoffice_queue', on_message_callback=callback_backoffice, auto_ack=False)


    try:
        print("Esperando mensajes...")
        channel.start_consuming()
    except Exception as e:
        print(f"Error en la conexión: {e}")
    finally:
        if channel.is_open:
            channel.close()
        connection.close()

 
# para ejecutar este módulo, se debe ejecutar el siguiente comando en la terminal: python -m pagos.consumidor_rabbitmq
#if __name__ == '__main__':
#    escuchar_topicos()