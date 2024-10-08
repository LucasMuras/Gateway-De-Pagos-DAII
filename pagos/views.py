from django.shortcuts import render, redirect
from .forms import PagoForm
from .rabbitmq import escuchar_reserva
import threading
from .models import Pagador, Destinatario

from django.http import JsonResponse
from .productor import enviar_reserva
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import  get_object_or_404

# Variable global para almacenar los datos de la reserva
reserva_datos = {}

def iniciar_escucha():
    """Inicia la escucha de RabbitMQ en un hilo separado."""
    escuchar_reserva()

# Inicia la escucha de RabbitMQ cuando arranca la aplicación
threading.Thread(target=iniciar_escucha, daemon=True).start()

def pago(request):
   
    # Obtén la última reserva creada
    pagador = Pagador.objects.last()
    destinatario = Destinatario.objects.last()

    if pagador is None:
        return render(request, 'pagos/pago.html', {'error': 'No se encontró ninguna reserva.'})


    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            # Aquí puedes procesar los datos del formulario
            # Por ejemplo, guardar el método de pago en la base de datos
            metodo_pago = form.cleaned_data['nombre_metodo']
            numero_tarjeta = form.cleaned_data['numero_tarjeta']
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            cvv = form.cleaned_data['cvv']
            # Aquí guardas los datos en la base de datos según tu modelo
            
            return redirect('nombre_de_la_vista_donde_redirigir')
    else:
        form = PagoForm()

    return render(request, 'pagos/pago.html', {'form': form, 'reserva':pagador, 'destinatario':destinatario})

@csrf_exempt
def crear_reserva(request):
    if request.method == 'POST':
        # Datos hardcodeados para el pagador y destinatario
        pagador = Pagador(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@example.com",
            telefono="123456789"
        )
        
        destinatario = Destinatario(
            nombre="Tienda XYZ"
        )

        # Suponiendo que el monto es enviado desde el formulario
        monto = float(request.POST.get('monto', 100.00))  # Valor por defecto si no se proporciona

        # Enviar la reserva utilizando los objetos
        enviar_reserva(pagador, destinatario, monto)

        return JsonResponse({'mensaje': 'Reserva enviada'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)