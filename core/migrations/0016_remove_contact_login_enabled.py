# Generated by Django 5.0.3 on 2024-04-08 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_vehicle_is_loaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='login_enabled',
        ),
    ]
