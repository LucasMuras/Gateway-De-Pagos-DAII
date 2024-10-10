import json
from ..models import Pagador, Destinatario, Transaccion

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

    transaccion_semi = Transaccion.objects.create(
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


def iniciar_transaccion():
    return

