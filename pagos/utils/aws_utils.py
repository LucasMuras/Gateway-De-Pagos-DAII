# aws_utils.py

#no usar aun

import boto3
import json

def enviar_evento_reserva(pagador, destinatario, monto):
    sns_client = boto3.client('sns', region_name='us-east-1')
    mensaje = {
        "evento": "reservaIniciada",
        "pagador": pagador,
        "destinatario": destinatario,
        "monto": monto
    }
    response = sns_client.publish(
        TopicArn='arn:aws:sns:us-east-1:559340055803:gatewaydepagos',
        Message=json.dumps(mensaje),
        Subject='reservaIniciada'
    )
    return response
