from django import forms

class PagoForm(forms.Form):
    tipo = forms.ChoiceField(choices=[('visa', 'Visa'), ('mastercard', 'MasterCard')])
    numero_tarjeta = forms.CharField(max_length=16, label='Número de Tarjeta', widget=forms.TextInput(attrs={'type': 'number'}))
    fecha_vencimiento = forms.DateField(label='Fecha de Vencimiento', widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}))
    cvv = forms.CharField(max_length=3, label='CVV', widget=forms.TextInput(attrs={'type': 'number'}))