# Generated by Django 5.1.1 on 2024-10-17 20:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0019_alter_tarjeta_dni'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaccion',
            name='es_reembolso',
        ),
    ]