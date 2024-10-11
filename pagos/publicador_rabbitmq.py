import pika, json
from django.conf import settings
import requests

#NO USARLO AUN

# Debe ser un endopint de Django que se encargue de enviar el evento de transacción al EDA
def enviar_evento_transaccion(transaccion):
    #connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
    #channel = connection.channel()
    
    #channel.queue_declare(queue='transaccion_queue')

    # Crear el mensaje del evento
    evento = {
        'estado': transaccion.estado,
        'descripcion': transaccion.descripcion,
        'fecha': transaccion.fecha.strftime('%Y-%m-%d %H:%M:%S'),
    }

    # Enviar el evento al EDA (este endpoint lo utilizará el EDA para recibir eventos de transacciones) 
    url = "http://localhost:3000/api/enviar-evento"
    response = requests.post(url, json=evento)
    
    if response.status_code == 200:
        print("Evento enviado con éxito")
    else:
        print("Error enviando evento")
    # Publicar el evento en la cola
    #channel.basic_publish(
    #    exchange='',
    #   routing_key='transaccion_queue',
    #    body=json.dumps(evento)
    #)

    # Cerrar la conexión
    #connection.close()

    print(f"Evento de transacción enviado al EDA.")