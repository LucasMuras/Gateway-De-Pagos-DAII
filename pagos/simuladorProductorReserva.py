import pika
import json
import time

def simulate_reserva_events(num_events):
    # Conexión a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar un Exchange de tipo 'topic'
    channel.exchange_declare(exchange='reservas_exchange', exchange_type='topic')

    for i in range(num_events):
        # Simular un evento de reserva
        reserva_event = {
            'reserva_id': f'{10000 + i}',  # Generar un ID único para cada reserva
            'user_id': f'{20000 + i}',      # Generar un ID único para cada usuario
            'amount': round(100 + i * 0.5, 2),  # Monto que varía ligeramente
            'status': 'confirmed'  # Puedes variar el estado si lo deseas
        }

        # Convertir el evento a JSON
        reserva_event_json = json.dumps(reserva_event)

        # Publicar el evento en el exchange con la clave de enrutamiento 'reservas.confirmada'
        channel.basic_publish(exchange='reservas_exchange', routing_key='reservas.nueva', body=reserva_event_json)
        print(f" [x] Simulated reserva event: {reserva_event_json}")

        # Esperar 1 segundo antes de enviar el siguiente evento
        time.sleep(1)

    # Cerrar conexión
    connection.close()

if __name__ == '__main__':
    simulate_reserva_events(50)  # Cambia el número aquí si quieres enviar más o menos eventos
