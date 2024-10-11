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
