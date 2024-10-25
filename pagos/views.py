from django.shortcuts import render
from .forms import PagoForm
from .models import Pagador, Destinatario, Tarjeta, MetodoPago, Transaccion
from .services.procesamiento_transaccion import iniciar_transaccion
import json, requests
#from .consumidor_rabbitmq import recibir_mensajes_sns
from .utils.utils import PagadorDic, DestinatarioDic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.libreria_sns_client import publish_to_topic, init_sns_client  # Asegúrate de importar tus funciones
from decouple import config
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE', '')})


@csrf_exempt 
def pago(request):
   
    # Obtenemos al pagador y destinario que estan en el momento para hacer la transaccion
    pagador = Pagador.objects.last()
    destinatario = Destinatario.objects.last()
    transaccion = Transaccion.objects.last()
    print(transaccion)

    if pagador is None or destinatario is None: 
        return render(request, 'pagos/pago.html', {'error': 'No se encontró ninguna reserva.'})

    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        form = PagoForm(data)
        print(request.POST, form.is_valid())
        if form.is_valid():
            # Nos guardamos los objetos que implican la transaccion
            en_cuotas = data.get('en_cuotas')
            tipo_metodo_pago = data.get('tipo_metodo_pago')
            cantidad_cuotas = data.get('cantidad_cuotas')
            dni = data.get('dni')
            numero = data.get('numero_tarjeta')
            fecha_vencimiento = data.get('fecha_vencimiento')
            cvv = data.get('cvv')
            tipo_tarjeta = data.get('tipo_tarjeta')
            nombre_titular = data.get('nombre_titular')

            tarjeta = Tarjeta.objects.create(
                nombre_titular = nombre_titular,
                dni = dni,
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
            transaccion_completa_exitosa, asunto = iniciar_transaccion(transaccion)
            print(transaccion_completa_exitosa)

            #Aun no, ver bien el puerto, dice 3000 deberia ser 8000
            #enviar_evento_transaccion(transaccion)

            if (transaccion_completa_exitosa == True):
                return JsonResponse({'status': 'Transacción exitosa', 'asunto': asunto}, status=200)
            else:
                return JsonResponse({'status': 'Transacción fallida', 'asunto': asunto}, status=400)
        else:
            #form = PagoForm(request.POST)
            print("invalido")
            form = PagoForm(data)
            return JsonResponse({'error': 'Datos de formulario inválidos', 'detalles': form.errors}, status=400)
    form =  PagoForm(request.POST)
    return render(request, 'pagos/pago.html', {'form': form, 'reserva':pagador, 'destinatario':destinatario, 'transaccion':transaccion})


def detallesTransaccion(request):
    if request.method == 'GET':
        transaccion = Transaccion.objects.last()
        if transaccion:
            transaccion_data = {
                'nombre_destinatario': transaccion.destinatario.nombre,
                'monto': transaccion.monto,
                'descripcion': transaccion.descripcion
            }
            return JsonResponse(transaccion_data)
        else:
            return JsonResponse({'error': 'No hay transacciones disponibles.'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    

# Se verifica la firma (estar conectado/suscripto al SNS) si sí se procesa el evento
@csrf_exempt
def sns_webhook(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))
            message_type = body.get('Type')
            if message_type == 'SubscriptionConfirmation':
                token = body.get('Token')
                subscribe_url = body.get('SubscribeURL')
                #return JsonResponse({'subscribe_url': subscribe_url})
                if token and subscribe_url:
                    #print({'subscribe_url': subscribe_url, 'token': token})
                    response = requests.get(subscribe_url)

                    if (response.status_code == 200):
                         print('Suscripción confirmada')
                         return JsonResponse({'status': 'Suscripción confirmada'})
                    else:
                        print('Suscripción no confirmada')
                        return JsonResponse({'error': 'No se pudo confirmar la suscripción'})
                else:
                    return JsonResponse({'error': 'Faltan parámetros para confirmar la suscripción'}, status=400)
            elif message_type == 'Notification':
                print('holaa')
                event = json.loads(request.body)
                print(event)
                #recibir_mensajes_sns(event)
                return JsonResponse({'mensaje': 'Evento procesado'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Cuerpo de solicitud no es JSON'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Simulacion reserva creada/iniciada
@csrf_exempt
def crear_reserva(request):
    if request.method == 'POST':
        # Datos hardcodeados para el pagador y destinatario
        pagador = PagadorDic(
            id_externa=1,
            nombre="Rodrigo",
            apellido="Nutriales",
            dni=88447755,
            email="rod.nut@example.com",
        )
        
        destinatario = DestinatarioDic(
            id_externa=1,
            nombre="Tienda Merequetengue",
            email="m@gmail.com"
        )
        print(destinatario, "sadsakldnas")

        # Suponiendo que el monto es enviado desde el formulario
        monto = float(request.POST.get('monto', 100.00))  # Valor por defecto si no se proporciona

        cuerpo_mensaje = {
            'pagador': pagador.to_dict(),
            'destinatario': destinatario.to_dict(),
            'monto': monto
        }

        # Credenciales de AWS SNS
        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
        AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
        AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='us-east-1')

        sns_client = init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)
        # Enviar el evento al tópico SNS
        publish_to_topic(sns_client, config('TOPIC_ARN_RESERVA'), 'reservaIniciada', cuerpo_mensaje)

        return JsonResponse({'mensaje': 'Reserva enviada'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Simulacion reembolso
@csrf_exempt
def reembolso(request):
    if request.method == 'POST':
        # Datos hardcodeados para el pagador y destinatario
        pagador = PagadorDic(
            id_externa=1,
            nombre="Rodrigo",
            apellido="Nutriales",
            dni=88447755,
            email="rod.nut@example.com",
        )
        
        destinatario = DestinatarioDic(
            id_externa=1,
            nombre="Tienda Merequetengue",
            email="m@gmail.com"
        )

        # Suponiendo que el monto es enviado desde el formulario
        monto = float(request.POST.get('monto', 100.00))  # Valor por defecto si no se proporciona

        cuerpo_mensaje = {
            'pagador': pagador.to_dict(),
            'destinatario': destinatario.to_dict(),
            'monto': monto,
            'descripcion': 'Reembolso por cancelación de reserva'
        }

        # Credenciales de AWS SNS
        AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
        AWS_SESSION_TOKEN = config('AWS_SESSION_TOKEN')
        AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='us-east-1')

        sns_client = init_sns_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, AWS_DEFAULT_REGION)
        # Enviar el evento al tópico SNS
        publish_to_topic(sns_client, config('TOPIC_ARN_RESERVA'), 'reservaCancelada', cuerpo_mensaje)

        return JsonResponse({'mensaje': 'Reembolso enviado'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)