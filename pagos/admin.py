from django.contrib import admin
from .models import MetodoPago, Pagador, Destinatario, Transaccion, Tarjeta

admin.site.register(MetodoPago)
admin.site.register(Pagador)
admin.site.register(Destinatario)
admin.site.register(Transaccion)
admin.site.register(Tarjeta)