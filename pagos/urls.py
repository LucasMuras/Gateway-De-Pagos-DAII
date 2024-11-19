from django.urls import path
from .views import pago, crear_reserva, sns_webhook, reembolso, detallesTransaccion, get_csrf_token

urlpatterns = [
    path('pago/<int:transaccion_id>/', pago, name='pago'),
    path('crear-reserva/', crear_reserva, name='crear_reserva'),  # URL para la vista de crear reserva
    path('sns-webhook/', sns_webhook, name='sns_webhook'),  # URL para la vista de webhook de SNS (SIN USO)
    path('reembolso/', reembolso, name='reembolso'),  # URL para la vista de crear reserva
    path('detalle/<int:transaccion_id>/', detallesTransaccion, name='detalle'),  # URL para obtener detalles de transaccion iniciada / reserva
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]