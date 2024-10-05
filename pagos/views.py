from django.http import JsonResponse
from .producer import send_payment_message

def process_payment_view(request):
    # Supón que aquí procesas el pago y obtienes la información del pago
    payment_info = "Pago exitoso con ID 12345"
    
    # Llamar al productor para enviar el mensaje a RabbitMQ
    send_payment_message(payment_info)

    # Responder con un mensaje de éxito
    return JsonResponse({'status': 'Payment processed and message sent to RabbitMQ'})
