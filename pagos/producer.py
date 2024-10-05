import pika

def send_payment_message(payment_info):
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola si no existe
    channel.queue_declare(queue='payments')

    # Publicar mensaje
    channel.basic_publish(exchange='', routing_key='payments', body=payment_info)
    print(f" [x] Sent payment info: {payment_info}")

    # Cerrar conexión
    connection.close()
