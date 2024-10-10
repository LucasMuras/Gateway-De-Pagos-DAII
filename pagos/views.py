from django.shortcuts import render, redirect
from .forms import PagoForm
from .rabbitmq import escuchar_topicos
import threading
from .models import Pagador, Destinatario, Tarjeta, MetodoPago, Transaccion
from .services.procesamiento_transaccion import iniciar_transaccion

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
    transaccion = Transaccion.objects.last()
    print(transaccion)

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
                nombre_titular = (pagador.nombre + " " + pagador.apellido).upper(),
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

            # hacer transaccion completa
            transaccion.descripcion = "Transaccion Iniciada"
            transaccion.metodo_pago = metodo_pago
            transaccion.estado = 'iniciado'
            transaccion.save()


            print(pagador.nombre)
            print(en_cuotas)
            print(numero)

            # procesar pago
            transaccion_completa_exitosa = iniciar_transaccion(transaccion)
            print(transaccion_completa_exitosa)
            if (transaccion_completa_exitosa == True):
                return render(request, 'pagos/pago_exitoso.html')
            else:
                return render(request, 'pagos/pago_fallido.html')
            
        
        else:
            form = PagoForm(request.POST)
            print("invalido")
            form = PagoForm()
    form =  PagoForm(request.POST)
    return render(request, 'pagos/pago.html', {'form': form, 'reserva':pagador, 'destinatario':destinatario, 'transaccion':transaccion})

@csrf_exempt
def crear_reserva(request):
    if request.method == 'POST':
        # Datos hardcodeados para el pagador y destinatario
        pagador = Pagador(
            id_externa=1,
            nombre="Rodrigo",
            apellido="Nutriales",
            dni=88447755,
            email="rod.nut@example.com",
        )
        
        destinatario = Destinatario(
            id_externa=1,
            nombre="Tienda Merequetengue",
            email="m@gmail.com"
        )

        # Suponiendo que el monto es enviado desde el formulario
        monto = float(request.POST.get('monto', 100.00))  # Valor por defecto si no se proporciona

        # Enviar la reserva utilizando los objetos
        enviar_reserva(pagador, destinatario, monto)

        return JsonResponse({'mensaje': 'Reserva enviada'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)