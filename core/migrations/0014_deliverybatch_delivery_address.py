# Generated by Django 5.0.3 on 2024-04-04 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_driver_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverybatch',
            name='delivery_address',
            field=models.TextField(default='Flat 301 National Nandanam, Palace Road, Edappally Erunakulam, Kerala India'),
            preserve_default=False,
        ),
    ]