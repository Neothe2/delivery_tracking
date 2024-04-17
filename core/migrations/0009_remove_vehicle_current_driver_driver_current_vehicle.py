# Generated by Django 5.0.3 on 2024-04-04 02:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_driver_current_vehicle_vehicle_current_driver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='current_driver',
        ),
        migrations.AddField(
            model_name='driver',
            name='current_vehicle',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_driver', to='core.vehicle'),
        ),
    ]