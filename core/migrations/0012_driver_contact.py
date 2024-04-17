# Generated by Django 5.0.3 on 2024-04-04 04:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_vehicle_current_driver_driver_current_vehicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='contact',
            field=models.OneToOneField(default=17, on_delete=django.db.models.deletion.CASCADE, related_name='driver', to='core.contact'),
            preserve_default=False,
        ),
    ]
