# aws_utils.py

import boto3, json
from decouple import config

# Configuración de AWS
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='us-east-1')
print(AWS_SESSION_TOKEN)

def enviar_evento_reserva(pagador, destinatario, monto):
    sns_client = boto3.client(
        'sns',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION)
    mensaje = {
        "evento": "reservaIniciada",
        "pagador": pagador,
        "destinatario": destinatario,
        "monto": monto
    }
    response = sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:559340055803:reserva',
        Message=json.dumps(mensaje),
        Subject='reservaIniciada'
    )
    return response
