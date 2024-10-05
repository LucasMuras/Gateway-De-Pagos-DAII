import pika
import json

def send_payment_message(payment_info):
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Publicar mensaje
    channel.basic_publish(exchange='payments_exchange', routing_key='payments.processed', body=payment_info)
    print(f" [x] Sent payment info: {payment_info}")

def process_reserva_event(ch, method, properties, body):
    # Procesar el evento de reserva
    reserva_event = json.loads(body)
    print(f" [x] Received reserva event: {reserva_event}")

    # Aquí podrías realizar el procesamiento de la reserva
    # Supongamos que quieres enviar un evento de pago después de procesar la reserva
    payment_info = json.dumps({
        'payment_id': f'PAY-{reserva_event["reserva_id"]}',
        'amount': reserva_event['amount'],
        'user_id': reserva_event['user_id'],
        'status': 'processed'
    })

    # Llamar a la función para enviar el mensaje de pago
    send_payment_message(payment_info)

def process_payment_event(ch, method, properties, body):
    # Procesar el evento de pago
    payment_event = json.loads(body)
    print(f" [x] Received payment info: {payment_event}")

def start_consumer():
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar el Exchange de reservas
    channel.exchange_declare(exchange='reservas_exchange', exchange_type='topic')

    # Declarar el Exchange de pagos
    channel.exchange_declare(exchange='payments_exchange', exchange_type='topic')

    # Declarar las colas si no existen
    channel.queue_declare(queue='reservas')
    channel.queue_declare(queue='payments')

    # Enlazar las colas a los exchanges
    channel.queue_bind(exchange='reservas_exchange', queue='reservas', routing_key='reservas.*')
    channel.queue_bind(exchange='payments_exchange', queue='payments', routing_key='payments.processed')

    # Configurar los consumidores
    channel.basic_consume(queue='reservas', on_message_callback=process_reserva_event, auto_ack=True)
    channel.basic_consume(queue='payments', on_message_callback=process_payment_event, auto_ack=True)

    print(' [*] Waiting for payment events. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()
