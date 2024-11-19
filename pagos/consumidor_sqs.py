import boto3, json
from .services.procesamiento_transaccion import guardar_entidades, iniciar_reembolso
from decouple import config
import time

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='us-east-1')

# Inicializar el cliente SQS
def init_sqs_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION):
    sqs_client = boto3.client(
        'sqs',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION)
    return sqs_client

# Recibe un mensaje de una cola SQS
def escuchar_sqs_mensajes(queue_url, sqs_client):
    while True:
        try:
            # Recibe mensajes de la cola
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,  # Número máximo de mensajes por lote
                WaitTimeSeconds=20  # Espera hasta que haya mensajes en la cola (long polling)
            )
            messages = response.get('Messages', [])
            print(messages)
            if messages:
                for message in messages:
                    # Procesar cada mensaje recibido
                    procesar_mensaje_sqs(message, queue_url)
                    
                    # Eliminar el mensaje de la cola una vez procesado
                    sqs_client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
            else:
                print("No hay mensajes en la cola, esperando...")
                
        except Exception as e:
            print(f"Error al recibir mensajes de SQS: {e}")
        time.sleep(5)  # Esperar antes de intentar recibir mensajes nuevamente


# Procesar un mensaje de SQS recibido
def procesar_mensaje_sqs(message, queue_url):
    try:
        body = message['Body']
        #sqs_message = json.loads(body)  # Convertir cadena JSON a diccionario Python
        receipt_handle = message['ReceiptHandle']

        # Procesar el cuerpo del mensaje
        sqs_message_dict = json.loads(body) #dict
        print('mensaje', sqs_message_dict)
        sns_topic = sqs_message_dict.get('TopicArn', '')
        print('topic', sns_topic)
        sns_event_type = sqs_message_dict.get('Subject', '')
        sns_message = sqs_message_dict.get('Message', '')
        print('SNSMESAGEs', sns_message)

        if 'reserva' in sns_topic:
            if 'reservation-created' in sns_event_type:
                print(f"Reserva creada: {sns_message}")
                transaccion = guardar_entidades(sns_message, 'transaccion', 'reserva')
                #enviar_id_transaccion(transaccion)
            elif 'reservation-updated' in sns_event_type:
                print(f"Reserva cancelada: {sns_message}")
                reembolso = guardar_entidades(sns_message, 'reembolso', 'reserva')
                iniciar_reembolso(reembolso)
            else:
                print(f"Evento no manejado: {sns_message}")
        elif 'backoffice' in sns_topic:
            if 'reservation-updated' in sns_event_type:
                print(f"Reserva cancelada: {sns_message}")
                reembolso = guardar_entidades(sns_message, 'reembolso', 'backoffice')
                iniciar_reembolso(reembolso)
            else:
                print(f"Evento no manejado: {sns_message}")

        # Eliminar el mensaje de la cola tras procesarlo exitosamente
        sqs = init_sqs_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        print(f"Mensaje eliminado de la cola: {body}")

    except Exception as e:
        print(f"Error procesando el mensaje de SQS: {e}")
