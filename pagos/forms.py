from django import forms
from datetime import datetime

class PagoForm(forms.Form):
    dni = forms.CharField(max_length=8, label='DNI', widget=forms.TextInput(attrs={'type': 'number'}))
    #tarjeta
    tipo_tarjeta = forms.ChoiceField(choices=[('visa', 'Visa'), ('mastercard', 'MasterCard')])
    numero_tarjeta = forms.CharField(max_length=16, label='Número de Tarjeta', widget=forms.TextInput(attrs={'type': 'number'}))
    fecha_vencimiento = forms.DateField(label='Fecha de Vencimiento', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    cvv = forms.CharField(max_length=3, label='CVV', widget=forms.TextInput(attrs={'type': 'number'}))
    
    tipo_metodo_pago = forms.ChoiceField(choices=[('tarjeta', 'Tarjeta'), ('mp', 'MP')])
    cuotas = forms.BooleanField(required=False, label='¿Cuotas?', widget=forms.CheckboxInput())
    cantidad_cuotas = forms.IntegerField(required=False, label='Cantidad de Cuotas', min_value=1, max_value=24)
