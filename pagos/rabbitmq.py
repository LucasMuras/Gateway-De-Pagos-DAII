import pika

def conectar_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='reservas', exchange_type='topic')
    return connection, channel

def callback(ch, method, properties, body):
    # Este callback se ejecuta cuando se recibe un mensaje en el tema 'reservaIniciada'
    mensaje = body.decode()
    # Aquí puedes procesar el mensaje (por ejemplo, parsear el JSON)
    print(f"Mensaje recibido: {mensaje}")

def escuchar_reserva():
    connection, channel = conectar_rabbitmq()
    channel.queue_declare(queue='reserva_queue')
    channel.queue_bind(exchange='reservas', queue='reserva_queue', routing_key='reservaIniciada')

    channel.basic_consume(queue='reserva_queue', on_message_callback=callback, auto_ack=True)

    print('Esperando mensajes. Para salir presiona CTRL+C')
    channel.start_consuming()
