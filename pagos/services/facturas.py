from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from decouple import config
from datetime import timedelta  
import base64

def calcular_ultima_fecha_cuota(fecha, cantidad_cuotas):
    if (cantidad_cuotas != None):
        return fecha + timedelta(days=30 * cantidad_cuotas)
    else:
        return 'No corresponde'
    
def calcular_subtotal(monto, cantidad_cuotas):
    if (cantidad_cuotas != None):
        return round(monto / cantidad_cuotas, 2)
    else:
        return monto

# factura para el cliente
def generar_factura_tipo_B(template_src, transaccion):
    context_dict = {
        'fecha_hoy': transaccion.fecha,
        'fecha_ultima_cuota':  calcular_ultima_fecha_cuota(transaccion.fecha, transaccion.metodo_pago.cuotas),
        'nombre_destinatario': transaccion.destinatario.name,
        'cantidad_cuotas': transaccion.metodo_pago.cuotas,
        'subtotal_primera_cuota': calcular_subtotal(transaccion.monto, transaccion.metodo_pago.cuotas),
        'total': transaccion.monto,
        'metodo_pago': transaccion.metodo_pago.tipo,
        'ultimos_numero_tarjeta': transaccion.metodo_pago.tarjeta.numero[-4:],
        'fecha_vencimiento_tarjeta': transaccion.metodo_pago.tarjeta.fecha_vencimiento,
        'tipo_tarjeta': transaccion.metodo_pago.tarjeta.tipo,
        'email_destinatario': transaccion.destinatario.email,
    }
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

# factura para el vendedor
def generar_factura_tipo_A(template_src, transaccion):
    context_dict = {
        'fecha_hoy': transaccion.fecha,
        'fecha_ultima_cuota':  calcular_ultima_fecha_cuota(transaccion.fecha, transaccion.metodo_pago.cuotas),
        'nombre_destinatario': transaccion.destinatario.name,
        'cantidad_cuotas': transaccion.metodo_pago.cuotas,
        'subtotal_primera_cuota': calcular_subtotal(transaccion.monto, transaccion.metodo_pago.cuotas),
        'total': transaccion.monto,
        'metodo_pago': transaccion.metodo_pago.tipo,
        'ultimos_numero_tarjeta': transaccion.metodo_pago.tarjeta.numero[-4:],
        'fecha_vencimiento_tarjeta': transaccion.metodo_pago.tarjeta.fecha_vencimiento,
        'tipo_tarjeta': transaccion.metodo_pago.tarjeta.tipo,
        'nombre_pagador': transaccion.pagador.name,
        'email_pagador': transaccion.pagador.email,
    }
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

# Nota de credito para el cliente en caso de devolucion por cancelacion
def generar_nota_credito(template_src, reembolso):
    context_dict = {
        'fecha_hoy': reembolso.fecha,
        'nombre_destinatario': reembolso.destinatario.name,
        'monto': reembolso.monto,
        'nombre_pagador': reembolso.pagador.name,
        'descripcion': reembolso.descripcion,
    }
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None


# envio de facturas por email de cada participante
# Ambas facturas al destinatario y la de tipo B solo al cliente
def enviar_pdf_por_email_pagador(factura_tipo_B_pdf, mail_pagador):
    # Crear el mensaje de correo electrónico
    email = EmailMessage(
        'Tu factura',
        'Adjuntamos la factura que has solicitado.',
        config('EMAIL_HOST_USER'),  # from
        [mail_pagador],  # to
    )

    print(email)

    # Adjuntar el PDF si se generó correctamente
    if factura_tipo_B_pdf:
        email.attach('factura.pdf', factura_tipo_B_pdf, 'application/pdf')

    try:
        # Enviar el correo
        email.send()
        print("El correo se ha enviado correctamente.")
    except Exception as e:
        # Manejar la excepción
        print(f"Error al enviar el correo: {e}")


def enviar_pdf_por_email_destinatario(factura_tipo_A_pdf, factura_tipo_B_pdf, mail_destinatario):
    # Crear el mensaje de correo electrónico
    email = EmailMessage(
        'Tu factura',
        'Adjuntamos la factura que has solicitado.',
        config('EMAIL_HOST_USER'), #from
        [mail_destinatario], #to
    )

    # Adjuntar el PDF si se generó correctamente
    if factura_tipo_A_pdf:
        email.attach('factura_tipo_A.pdf', factura_tipo_A_pdf, 'application/pdf')

    if factura_tipo_B_pdf:
        email.attach('factura_tipo_B.pdf', factura_tipo_B_pdf, 'application/pdf')

    # Enviar el correo
    email.send()


def enviar_nota_pdf_por_email_pagador(nota_pdf, mail_pagador):
    email = EmailMessage(
        'Tu nota de credito',
        'Adjuntamos la nota de credito que has solicitado.',
        config('EMAIL_HOST_USER'),
        [mail_pagador],  
    )

    if nota_pdf:
        email.attach('nota.pdf', nota_pdf, 'application/pdf')

    email.send()
    