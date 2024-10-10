import json, os
from ..models import Pagador, Destinatario, Transaccion
from . import validaciones

def guardar_entidades(mensaje):
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

    transaccion = Transaccion.objects.create(
        pagador = pagador,
        destinatario = destinatario,
        monto = data['monto'],
        descripcion = None,
        metodo_pago = None,
        fecha = None,
        estado = 'pendiente',
        es_reembolso = False
    )



    print("Reserva recibida:")
    print(f"Pagador: {pagador.nombre} {pagador.apellido}")
    print(f"Email: {pagador.email}")
    print(f"Destinatario: {destinatario.nombre}")

    # No se redirige en este caso, ya que estamos en el contexto de un consumidor


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


    # Validacion de tarjeta
    validacion_vencimiento = validaciones.validar_vencimiento(tarjeta_existente)
    validacion_estado = validaciones.validar_estado(tarjeta_existente)

    if (validacion_vencimiento == False or validacion_estado == False):
        print("Tarjeta invalida")
        transaccion.estado = 'fallido'
        return False


    # Validacion de saldo suficiente
    monto = transaccion.monto
    validacion_monto = validaciones.validar_monto(tarjeta_existente, monto)

    if (validacion_monto == False):
        print("El saldo actual de su tarjeta es insuficiente")
        transaccion.estado = 'fallido'
        return False
    else:
        tarjeta_existente['saldo'] = float(tarjeta_existente['saldo']) - float(monto)
        with open(ruta_tarjetas_json, 'w') as archivo:
            json.dump(tarjetas_json, archivo, indent=4)  # Guardar con formato
        print("Transaccion exitosa")
        transaccion.estado = 'valido'
        transaccion.save()
        return True


