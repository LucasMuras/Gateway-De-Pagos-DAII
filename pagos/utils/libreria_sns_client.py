import boto3, json
from botocore.exceptions import ClientError
from decouple import config
import requests

# Cargar credenciales desde .env
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION')

# Inicializar el cliente SNS
def init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION):
    sns_client = boto3.client(
        'sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION)
    return sns_client

# Inicializar el cliente de WebSocket
def init_websocket_client():
    return boto3.client(
        'apigatewaymanagementapi',
        endpoint_url='https://25zb4cxwg1.execute-api.us-east-1.amazonaws.com/dev',
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN
    )

# Función para enviar mensaje a WebSocket
def publish_to_websocket(connection_id, message, websocket_client):
    try:
        print(f"Enviando mensaje al WebSocket con ConnectionId: {connection_id}")
        response = websocket_client.post_to_connection(
            Data=message.encode("utf-8"),  # Corrigiendo encoding
            ConnectionId=connection_id
        )
        return response
    except Exception as e:
        print(f"Error publicando en WebSocket: {e}")
        raise


# Publicar un mensaje en un tópico de SNS
def publish_to_topic(sns_client, topic_arn, event_name, message):
    print(f"Publicando mensaje en el tópico {topic_arn}")
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=event_name
        )
        
        # Si la publicación fue exitosa, se obtiene el status code
        status = "success" if response['ResponseMetadata']['HTTPStatusCode'] == 200 else "error"

    except Exception as e:
        print(f"Error al publicar el mensaje: {e}")
        status = "error"  # Asignar "error" si ocurre una excepción

    websocket_client = init_websocket_client();

    # Obtener los connection IDs desde los endpoints
    connection_id_express = get_last_connection_id('https://eda-daii-production-9f47.up.railway.app/api/connection-id/server/last')
    connection_id_react = get_last_connection_id('https://eda-daii-production-9f47.up.railway.app/api/connection-id/front/last')

    connections_id = [connection_id_express, connection_id_react]
    print(connections_id, 'CONECTION IDS')
    
    for connection_client_id in connections_id:
        messagews = {
            "topico": topic_arn.split(":")[-1],
            "event_name": event_name,
            "body": message,
            "connection_id": connection_client_id,
            "status": status,
            "message": "actualizacion"
        }
        event = {
            "connectionId": connection_client_id,
            "message": json.dumps(messagews)
        }

        connection_id = event['connectionId']
        message_ws = event['message']

        publish_to_websocket(connection_id, message_ws, websocket_client)

    return response


# Suscripcion a un tópico de SNS
def subscribe_to_topic(sns_client, topic_arn_to_suscribe, protocol, direction):
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn_to_suscribe,
            Protocol=protocol,  # Ej: 'https', 'email', 'sms', etc.
            Endpoint=direction   # La URL o dirección donde se recibirán los mensajes
        )
        print(f"Suscripción exitosa: {response}")
        return response
    except ClientError as e:
        print(f"Error en la suscripción: {e}")
        raise e
    

# Función para obtener el último connectionId de un endpoint
def get_last_connection_id(endpoint_url):
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()  # Lanza un error si la respuesta es un código de estado 4xx o 5xx
        data = response.json()
        return data.get('connection_id')  # Asumiendo que la respuesta tiene un campo 'connectionId'
    except Exception as e:
        print(f"Error al obtener el connectionId de {endpoint_url}: {e}")
        return None