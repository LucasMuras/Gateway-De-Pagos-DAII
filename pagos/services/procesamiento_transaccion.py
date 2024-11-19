import json, os
from ..models import Pagador, Destinatario, Transaccion, Reembolso
from . import validaciones, facturas
from django.utils import timezone
from ..utils.libreria_sns_client import publish_to_topic, init_sns_client
from decouple import config
from ..utils.utils import TransaccionDic, PagadorDic, DestinatarioDic, MetodoPagoDic, TarjetaDic

# Cargar credenciales desde .env
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION')

def guardar_entidades(mensaje, caso, topico):
    print('ENTOOOO')
    # Convertir el mensaje a un diccionario (asumiendo JSON)
    data = json.loads(mensaje)
    #print("DATATATA", data['user_profile'].get('id'), data)

   # Crear y guardar los objetos Pagador y Destinatario
    if (topico == 'reserva'):
        pagador = Pagador.objects.create(
            id_external=data['user_profile'].get('id'),
            name=data['user_profile'].get('name'),
            surname=data['user_profile'].get('surname'),
            phone=data['user_profile'].get('phone'),
            document=data['user_profile'].get('document'),
            birth_date=data['user_profile'].get('birth_date'),
            email=data['user_profile'].get('email'),
        )

        destinatario = Destinatario.objects.create(
            id_external=data['room'].get('id'),
            hotel=data['room'].get('hotel').get('id'),
            floor=data['room'].get('floor'),
            name=data['room'].get('hotel').get('name'),
            price=data['room'].get('price'),
            state=data['room'].get('state'),
            double_beds_amount=data['room'].get('double_beds_amount'),
            single_beds_amount=data['room'].get('single_beds_amount'),
            images=data['room'].get('images'),
            email = data['room'].get('hotel').get('email')
        )

        if caso == 'transaccion':
            transaccion = Transaccion.objects.create(
                id_external = data['id'],
                room = data['room'].get('id'),
                start_date = data.get('start_date'),
                end_date = data.get('end_date'),
                #client = models.IntegerField(default=0)
                services = data.get('services'),
                pagador=pagador,
                destinatario=destinatario,
                monto=data.get('total_price'),  # Usa un valor por defecto
                metodo_pago=None,
                fecha=None,
                estado='pendiente',
            )
            return transaccion
        else:  # Asumimos que 'caso' es 'reembolso'
            reembolso = Reembolso.objects.create(
                id_external=data.get('id'),
                room=data['room'].get('id'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                client=data['user_profile'].get('id'),
                services=data['services'],
                pagador=pagador,
                destinatario=destinatario,
                monto=data.get('total_price'),  # Usa un valor por defecto
                descripcion="Cancelación de reserva",
                fecha=timezone.now(),
                estado='pendiente',
            )
            return reembolso
    else:
        pagador = Pagador.objects.create(
            id_external=data['client_info'].get('id'),
            name=data['client_info'].get('name'),
            surname=data['client_info'].get('surname'),
            phone=data['client_info'].get('phone'),
            document=data['client_info'].get('document'),
            birth_date=data['client_info'].get('birth_date'),
            email=data['client_info'].get('email'),
        )

        destinatario = Destinatario.objects.create(
            id_external=data.get('id'),
            hotel=data['room_info'].get('hotel'),
            floor=data['room_info'].get('floor'),
            name=data['room_info'].get('name'),
            price=data['room_info'].get('price'),
            state=data['room_info'].get('state'),
            double_beds_amount=data['room_info'].get('double_beds_amount'),
            single_beds_amount=data['room_info'].get('single_beds_amount'),
            images=data['room_info'].get('images'),
            #email = data['room_info'].get('email')
            )
        
        if caso == 'transaccion':
            transaccion = Transaccion.objects.create(
                id_external = data['id'],
                room = data['room'].get('id'),
                start_date = data.get('start_date'),
                end_date = data.get('end_date'),
                #client = models.IntegerField(default=0)
                services = data.get('services'),
                pagador=pagador,
                destinatario=destinatario,
                monto=data.get('total_price'),  # Usa un valor por defecto
                metodo_pago=None,
                fecha=None,
                estado='pendiente',
            )
            return transaccion
        else:  # Asumimos que 'caso' es 'reembolso'
            reembolso = Reembolso.objects.create(
                #id_external=data['id'],
                room=data.get('room'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                client=data.get('client_info').get('id'),
                services=data.get('services'),
                pagador=pagador,
                destinatario=destinatario,
                monto=data.get('total_price'),  # Usa un valor por defecto
                descripcion="Cancelación de reserva",
                fecha=timezone.now(),
                estado='pendiente',
            )
            return reembolso

    # No se redirige en este caso, ya que estamos en el contexto de un consumidor


# Enviar ID de la transaccion
def enviar_id_transaccion(transaccion):
    sns_client = init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)
    cuerpo_mensaje = {
        "id_transaction": transaccion.id_external,
    }
    publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'initiated-transaction', cuerpo_mensaje)
    return



# Manejo del pago
def iniciar_transaccion(transaccion):
    sns_client = init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)

    tarjeta = transaccion.metodo_pago.tarjeta
    
    ruta_tarjetas_json = os.path.join(
        os.path.dirname(__file__), '..', 'assets', 'tarjetas.json'
    )

    with open(ruta_tarjetas_json, 'r') as archivo:
        tarjetas_json = json.load(archivo)

    tarjeta_existente = {}
    for tarjeta_json in tarjetas_json:
        print(tarjeta.numero, tarjeta_json['numero'])
        if int(tarjeta.numero) == tarjeta_json['numero']:
            print("Tarjeta encontrada")
            tarjeta_existente = tarjeta_json
            break
        # else:
        #     print("Tarjeta no encontrada")
        #     transaccion.estado = 'fallido'
        #     return (False, "La tarjeta no existe")

    if (tarjeta_existente == {}):
        return (False, "La tarjeta no existe")
    else:
        # Validaciones
        validacion_dni = validaciones.validar_dni(tarjeta_existente, tarjeta)
        validacion_vencimiento = validaciones.validar_vencimiento(tarjeta_existente)
        validacion_estado = validaciones.validar_estado(tarjeta_existente)

        if (validacion_vencimiento == False or validacion_estado == False or validacion_dni == False):
            print("Tarjeta invalida")
            transaccion.estado = 'fallido'
            transaccion.fecha = timezone.now()
            transaccion.save()

            cuerpo_mensaje = {
                    "estado": transaccion.estado,
                    "descripcion": "La tarjeta no es válida"
                }   

            #Evento transaccion exitosa
            publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'failed-transaction', cuerpo_mensaje)
            
            return (False, transaccion.descripcion)
        else:
            print(transaccion.metodo_pago.en_cuotas)
            # Verifico si eligió cuotas o en un pago unico
            if (transaccion.metodo_pago.en_cuotas == True):
                monto = round(transaccion.monto / transaccion.metodo_pago.cuotas, 2)
                #print(monto)
            else:
                monto = transaccion.monto

            # Validacion de saldo suficiente para abonar
            validacion_monto = validaciones.validar_monto(tarjeta_existente, monto)

            if (validacion_monto == False):
                print("El saldo actual de su tarjeta es insuficiente")
                transaccion.estado = 'fallido'
                transaccion.fecha = timezone.now()

                cuerpo_mensaje = {
                    "estado": transaccion.estado,
                    "descripcion": "El saldo actual de su tarjeta es insuficiente"
                }   

                #Evento transaccion exitosa
                publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'failed-transaction', cuerpo_mensaje)

                return (False, "El saldo actual de su tarjeta es insuficiente")
            else:
                tarjeta_existente['saldo'] = round(float(tarjeta_existente['saldo']) - float(monto), 2)
                with open(ruta_tarjetas_json, 'w') as archivo:
                    json.dump(tarjetas_json, archivo, indent=4)
                print("Transaccion exitosa")
                transaccion.estado = 'valido'
                transaccion.fecha = timezone.now()
                #print(transaccion.fecha)
                transaccion.save()

                cuerpo_mensaje = {
                    "estado": transaccion.estado,
                    "redirect": "url",
                }   

                #Evento transaccion exitosa
                publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'valid-transaction', cuerpo_mensaje)

                # Generar y enviar facturas
                factura_tipo_A = facturas.generar_factura_tipo_A('pagos/factura_tipo_A.html', transaccion)
                factura_tipo_B = facturas.generar_factura_tipo_B('pagos/factura_tipo_B.html', transaccion)
                #print(factura_tipo_A, factura_tipo_B, 'nioincwecweiocnewicnweicnwienciowenciwenci')
                mail_pagador = transaccion.pagador.email
                mail_destinatario = transaccion.destinatario.email
                try:
                    facturas.enviar_pdf_por_email_pagador(factura_tipo_B, mail_pagador)
                    facturas.enviar_pdf_por_email_destinatario(factura_tipo_A, factura_tipo_B, mail_destinatario)
                except Exception as e:
                    print("Error al enviar los correos: AAAAAAAAAAAAAAAAAAAAAAAAAAKMDDDDDDDDDDDDDDDDDDDDDDCN", e)

                #Evento facturas enviadas
                cuerpo_mensaje = {
                    "descripcion": "Facturas tipo A y B enviadas",
                }   

                publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'facturaClienteGenerada', cuerpo_mensaje)
                publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'facturaAdministradorGenerada', cuerpo_mensaje)
                
                return (True, "Transaccion completada de manera exitosa, esté pendiente a su casilla de email donde se le enviara la factura correspondiente")
            

# Manejo de un reembolso debido a cancelacion
def iniciar_reembolso(reembolso):
    sns_client = init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)

    # No tenemos base de datos. Solo será crear la nota de credito y enviarla por email.
    print("REEEMBOLSOSOSOSO", reembolso.id_external, reembolso)
    #enviar evento de reembolso exitoso

    #publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'valid-reimbursement', cuerpo_mensaje)

    print('etnro')
    notaDeCredito = facturas.generar_nota_credito('pagos/nota_credito.html', reembolso)
    mail_pagador = reembolso.pagador.email
    facturas.enviar_nota_pdf_por_email_pagador(notaDeCredito, mail_pagador)

    #enviar evento de generacion de nota de credito
    cuerpo_mensaje = {
        "descripcion": "enviada",
    }   

    publish_to_topic(sns_client, config("TOPIC_ARN_GATEWAYDEPAGOS"), 'credit-note-generated', cuerpo_mensaje)

    return

    
        
    