# Por temas de formato

class PagadorDic:
    def __init__(self, id_externa, nombre, apellido, dni, email):
        self.id_externa = id_externa
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.email = email

    def to_dict(self):
        return {
            "id_externa": self.id_externa,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "dni": self.dni,
            "email": self.email,
        }

class DestinatarioDic:
    def __init__(self, id_externa, nombre, email):
        self.id_externa = id_externa
        self.nombre = nombre
        self.email = email

    def to_dict(self):
        return {
            "id_externa": self.id_externa,
            "nombre": self.nombre,
            "email": self.email,
        }



class TransaccionDic:
    def __init__(self, pagador, destinatario, monto, descripcion, metodo_pago, fecha, estado):
        self.pagador = pagador  # Debe ser un objeto PagadorDic
        self.destinatario = destinatario  # Debe ser un objeto DestinatarioDic
        self.monto = monto
        self.descripcion = descripcion
        self.metodo_pago = metodo_pago  # Puedes usar otro diccionario si necesitas
        self.fecha = fecha  # Esto puede ser un objeto datetime
        self.estado = estado

    def to_dict(self):
        return {
            "pagador": self.pagador.to_dict(),
            "destinatario": self.destinatario.to_dict(),
            "monto": str(self.monto),  # Convertir a str si es necesario
            "descripcion": self.descripcion,
            "metodo_pago": self.metodo_pago,  # Puede ser convertido si tienes un método para eso
            "fecha": self.fecha.isoformat(),  # Convertir a formato ISO si es un datetime
            "estado": self.estado,
        }
    

class MetodoPagoDic:
    def __init__(self, en_cuotas, tipo, cuotas, tarjeta):
        self.en_cuotas = en_cuotas
        self.tipo = tipo
        self.cuotas = cuotas  # Puede ser un entero
        self.tarjeta = tarjeta  # Puedes usar un objeto de tarjeta o su representación en dict

    def to_dict(self):
        return {
            "en_cuotas": self.en_cuotas,
            "tipo": self.tipo,
            "cuotas": self.cuotas,
            "tarjeta": self.tarjeta.to_dict(),  # Si tienes un método para convertir tarjeta a dict
        }
    

class TarjetaDic:
    def __init__(self, nombre_titular, dni, numero, fecha_vencimiento, cvv, tipo):
        self.nombre_titular = nombre_titular
        self.dni = dni
        self.numero = numero
        self.fecha_vencimiento = fecha_vencimiento
        self.cvv = cvv
        self.tipo = tipo

    def to_dict(self):
        return {
            "nombre_titular": self.nombre_titular,
            "dni": self.dni,
            "numero": self.numero,
            "fecha_vencimiento": str(self.fecha_vencimiento),  # Convertir a string si es un objeto Date
            "cvv": self.cvv,
            "tipo": self.tipo,
        }