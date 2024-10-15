from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from decouple import config

# factura para el cliente
def generar_factura_tipo_B(template_src, transaccion):
    context_dict = {
        'invoice_id': transaccion.id,
        'customer_name': transaccion.pagador.nombre,
        'date': transaccion.fecha,
        'items': [
            {'name': 'Producto 1', 'price': 50},
            {'name': 'Producto 2', 'price': 30}
        ],
        'total': 80,
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
        'invoice_id': transaccion.id,
        'customer_name': transaccion.pagador.nombre,
        'date': transaccion.fecha,
        'items': [
            {'name': 'Producto 1', 'price': 50},
            {'name': 'Producto 2', 'price': 30}
        ],
        'total': 80,
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

    # Adjuntar el PDF si se generó correctamente
    if factura_tipo_B_pdf:
        email.attach('factura.pdf', factura_tipo_B_pdf, 'application/pdf')

    # Enviar el correo
    email.send()


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