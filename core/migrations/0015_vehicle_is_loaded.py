# Generated by Django 5.0.3 on 2024-04-05 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_deliverybatch_delivery_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='is_loaded',
            field=models.BooleanField(default=False),
        ),
    ]