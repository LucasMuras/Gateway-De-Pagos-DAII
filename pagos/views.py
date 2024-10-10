from django.shortcuts import render, redirect
from .forms import PagoForm
from .rabbitmq import escuchar_topicos
import threading
from .models import Pagador, Destinatario, Tarjeta, MetodoPago, Transaccion

from django.http import JsonResponse
from .productor import enviar_reserva
from django.views.decorators.csrf import csrf_exempt
 
 
def iniciar_escucha():
    """Inicia la escucha de RabbitMQ en un hilo separado."""
    escuchar_topicos()

# Inicia la escucha de RabbitMQ cuando arranca la aplicación
threading.Thread(target=iniciar_escucha, daemon=True).start()

def pago(request):
   
    # Obtenemos al pagador y destinario que estan en el momento para hacer la transaccion
    pagador = Pagador.objects.last()
    destinatario = Destinatario.objects.last()
    transaccion_semi = Transaccion.objects.last()

    if pagador is None or destinatario is None:
        return render(request, 'pagos/pago.html', {'error': 'No se encontró ninguna reserva.'})

    if request.method == 'POST':
        form = PagoForm(request.POST)
        print(request.POST)
        if form.is_valid():
            # Nos guardamos los objetos que implican la transaccion
            en_cuotas = form.cleaned_data['cuotas']
            tipo_metodo_pago = form.cleaned_data['tipo_metodo_pago']
            cantidad_cuotas = form.cleaned_data['cantidad_cuotas']

            numero = form.cleaned_data['numero_tarjeta']
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            cvv = form.cleaned_data['cvv']
            tipo_tarjeta = form.cleaned_data['tipo_tarjeta']

            tarjeta = Tarjeta.objects.create(
                nombre_titular = pagador.nombre,
                numero = numero,
                fecha_vencimiento = fecha_vencimiento,
                cvv = cvv,
                tipo = tipo_tarjeta
            )

            metodo_pago = MetodoPago.objects.create(
                en_cuotas = en_cuotas,
                tipo = tipo_metodo_pago,
                cuotas = cantidad_cuotas if en_cuotas else None,
                tarjeta = tarjeta,
            )

            print(pagador.nombre)
            print(en_cuotas)
            print(numero)
            
            return render(request, 'pagos/pago_exito.html')
        
        else:
            form = PagoForm(request.POST)
            print("invalido")
            form = PagoForm()
    form =  PagoForm(request.POST)
    return render(request, 'pagos/pago.html', {'form': form, 'reserva':pagador, 'destinatario':destinatario, 'transaccion_semi':transaccion_semi})

@csrf_exempt
def crear_reserva(request):
    if request.method == 'POST':
        # Datos hardcodeados para el pagador y destinatario
        pagador = Pagador(
            id_externa=12345,
            nombre="Vicente",
            apellido="Vainilla",
            dni=12345678,
            email="mar.gon@example.com",
        )
        
        destinatario = Destinatario(
            id_externa=54321,
            nombre="Tienda LOL",
            email="xyz@gmail.com"
        )

        # Suponiendo que el monto es enviado desde el formulario
        monto = float(request.POST.get('monto', 100.00))  # Valor por defecto si no se proporciona

        # Enviar la reserva utilizando los objetos
        enviar_reserva(pagador, destinatario, monto)

        return JsonResponse({'mensaje': 'Reserva enviada'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)