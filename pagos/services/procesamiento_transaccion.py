import json, os
from ..models import Pagador, Destinatario, Transaccion, Reembolso
from . import validaciones, facturas
from django.utils import timezone

def guardar_entidades(mensaje, caso):
    # Convertir el mensaje a un diccionario (asumiendo JSON)
    data = json.loads(mensaje)

    # Crear y guardar los objetos Pagador y Destinatario
    pagador = Pagador.objects.create(
        id_externa=data['pagador']['id_externa'],
        nombre=data['pagador']['nombre'],
        apellido=data['pagador']['apellido'],
        dni=data['pagador']['dni'],
        email=data['pagador']['email'],
    )

    destinatario = Destinatario.objects.create(
        id_externa=data['destinatario']['id_externa'],
        nombre=data['destinatario']['nombre'],
        email=data['destinatario']['email'],
    )

    if (caso == 'transaccion'):
        transaccion = Transaccion.objects.create(
            pagador = pagador,
            destinatario = destinatario,
            monto = data['monto'],
            descripcion = None,
            metodo_pago = None,
            fecha = None,
            estado = 'pendiente',
        )
        return pagador, destinatario, transaccion
    else:
        reembolso = Reembolso.objects.create(
            pagador = pagador,
            destinatario = destinatario,
            monto = data['monto'],
            descripcion = data['descripcion'],
            fecha = timezone.now(),
            estado = 'pendiente',
        )
        return reembolso
    # No se redirige en este caso, ya que estamos en el contexto de un consumidor


# Manejo del pago
def iniciar_transaccion(transaccion):

    tarjeta = transaccion.metodo_pago.tarjeta
    
    ruta_tarjetas_json = os.path.join(
        os.path.dirname(__file__), '..', 'assets', 'tarjetas.json'
    )

    with open(ruta_tarjetas_json, 'r') as archivo:
        tarjetas_json = json.load(archivo)

    tarjeta_existente = {}
    for tarjeta_json in tarjetas_json:
        if int(tarjeta.numero) == tarjeta_json['numero']:
            print("Tarjeta encontrada")
            tarjeta_existente = tarjeta_json
            break
        else:
            print("Tarjeta no encontrada")
            transaccion.estado = 'fallido'
            return False

    # Validaciones
    validacion_dni = validaciones.validar_dni(tarjeta_existente, tarjeta)
    validacion_vencimiento = validaciones.validar_vencimiento(tarjeta_existente)
    validacion_estado = validaciones.validar_estado(tarjeta_existente)

    if (validacion_vencimiento == False or validacion_estado == False or validacion_dni == False):
        print("Tarjeta invalida")
        transaccion.estado = 'fallido'
        return False
    else:
        print(transaccion.metodo_pago.en_cuotas)
        # Verifico si eligió cuotas o en un pago unico
        if (transaccion.metodo_pago.en_cuotas == True):
            monto = round(transaccion.monto / transaccion.metodo_pago.cuotas, 2)
            print(monto)
        else:
            monto = transaccion.monto

        # Validacion de saldo suficiente para abonar
        validacion_monto = validaciones.validar_monto(tarjeta_existente, monto)

        if (validacion_monto == False):
            print("El saldo actual de su tarjeta es insuficiente")
            transaccion.estado = 'fallido'
            transaccion.fecha = timezone.now()
            transaccion.descripcion = "Transaccion fallida"
            return False
        else:
            tarjeta_existente['saldo'] = round(float(tarjeta_existente['saldo']) - float(monto), 2)
            with open(ruta_tarjetas_json, 'w') as archivo:
                json.dump(tarjetas_json, archivo, indent=4)
            print("Transaccion exitosa")
            transaccion.estado = 'valido'
            transaccion.fecha = timezone.now()
            print(transaccion.fecha)
            transaccion.descripcion = "Transaccion exitosa"
            transaccion.save()

            #Evento transaccion exitosa

            # Generar y enviar facturas
            factura_tipo_A = facturas.generar_factura_tipo_A('pagos/factura_tipo_A.html', transaccion)
            factura_tipo_B = facturas.generar_factura_tipo_B('pagos/factura_tipo_B.html', transaccion)

            mail_pagador = transaccion.pagador.email
            mail_destinatario = transaccion.destinatario.email
            facturas.enviar_pdf_por_email_pagador(factura_tipo_B, mail_pagador)
            facturas.enviar_pdf_por_email_destinatario(factura_tipo_A, factura_tipo_B, mail_destinatario)

            #Evento facturas enviadas

            return True
        

# Manejo de un reembolso debido a cancelacion
def iniciar_reembolso(reembolso):
    # No tenemos base de datos. Solo será crear la nota de credito y enviarla por email.

    #enviar evento de reembolso pendiente
    #enviar evento de reembolso exitoso
    print('etnro')
    notaDeCredito = facturas.generar_nota_credito('pagos/nota_credito.html', reembolso)
    mail_pagador = reembolso.pagador.email
    facturas.enviar_nota_pdf_por_email_pagador(notaDeCredito, mail_pagador)

    #enviar evento de generacion de nota de credito

    return

    
        
    