from datetime import datetime

 # Validar: que la tarjeta no esté vencida
def validar_vencimiento(tarjeta_existente):
    # Validar: que la tarjeta no esté vencida
    fecha_vencimiento = datetime.strptime(tarjeta_existente['fecha_vencimiento'], '%Y-%m-%d')

    if (fecha_vencimiento <= datetime.now()):
        return (False, "La tarjeta se encuentra vencida")
    else:
        return (True, "La tarjeta no se encuentra vencida")


 # Validar: que el estado de la tarjeta sea activa
def validar_estado(tarjeta_existente):
    if (tarjeta_existente['estado'] != 'activa'):
        return (False, "La tarjeta se encuentra inactiva")
    else:
        return (True, "Tarjeta válida")


 # Ejecutar si la tarjeta es válida
 # Validar si hay saldo suficiente para abonar el monto
def validar_monto(tarjeta_existente, monto):
    if (tarjeta_existente['saldo'] < monto):
        return (False, "Saldo insuficiente")
    else:
        return(True, "Saldo suficiente")