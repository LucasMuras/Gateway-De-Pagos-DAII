# Generated by Django 5.1.1 on 2024-10-09 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0009_metodopago_cuotas_metodopago_encuotas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagador',
            name='telefono',
        ),
    ]
