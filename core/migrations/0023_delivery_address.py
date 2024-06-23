# Generated by Django 5.0.6 on 2024-06-07 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_remove_proofofdelivery_delivery_batch_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='deliveries', to='core.address'),
            preserve_default=False,
        ),
    ]