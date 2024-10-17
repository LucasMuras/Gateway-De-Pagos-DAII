import boto3, json
from botocore.exceptions import ClientError

# Inicializar el cliente SNS
def init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION):
    sns_client = boto3.client(
        'sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION)
    return sns_client

# Publicar un mensaje en un tópico de SNS
def publish_to_topic(sns_client, topic_arn, event_name, message):
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        Subject=event_name
    )
    return response

# Suscripcion a un tópico de SNS
def subscribe_to_topic(sns_client, topic_arn_to_suscribe, protocol, endpoint):
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn_to_suscribe,
            Protocol=protocol,  # Ej: 'https', 'email', 'sms', etc.
            Endpoint=endpoint   # La URL o dirección donde se recibirán los mensajes
        )
        print(f"Suscripción exitosa: {response}")
        return response
    except ClientError as e:
        print(f"Error en la suscripción: {e}")
        raise e