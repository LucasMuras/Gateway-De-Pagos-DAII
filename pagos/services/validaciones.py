from datetime import datetime

# Validar: número de documento coincide con el de la tarjeta
def validar_dni(tarjeta_existente, tarjeta):
    print("ahber",tarjeta_existente['dni_titular'] != int(tarjeta.dni))
    if (int(tarjeta_existente['dni_titular']) != int(tarjeta.dni)):
        return False #"El DNI no coincide con el de la tarjeta")
    else:
        return True #"DNI válido")


# Validar: que la tarjeta no esté vencida
def validar_vencimiento(tarjeta_existente):
    # Validar: que la tarjeta no esté vencida
    fecha_vencimiento = datetime.strptime(tarjeta_existente['fecha_vencimiento'], '%Y-%m-%d')

    if (fecha_vencimiento <= datetime.now()):
        return False #"La tarjeta se encuentra vencida")
    else:
        return True # "La tarjeta no se encuentra vencida")


# Validar: que el estado de la tarjeta sea activa
def validar_estado(tarjeta_existente):
    if (tarjeta_existente['estado'] != 'activa'):
        return False #"La tarjeta se encuentra inactiva")
    else:
        return True #"Tarjeta válida")


# Ejecutar si la tarjeta es válida
# Validar si hay saldo suficiente para abonar el monto
def validar_monto(tarjeta_existente, monto):
    # Si es en un solo pago
    if (float(tarjeta_existente['saldo']) < float(monto)):
        print("holaa")
        return False
    else:
        return True