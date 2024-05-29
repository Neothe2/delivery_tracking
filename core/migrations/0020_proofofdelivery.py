# Generated by Django 5.0.6 on 2024-05-29 14:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_address_alter_deliverybatch_delivery_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProofOfDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature_image', models.ImageField(blank=True, upload_to='proof_of_delivery/')),
                ('image', models.ImageField(upload_to='proof_of_delivery/')),
                ('notes', models.TextField(blank=True)),
                ('delivery_batch', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='proof_of_delivery', to='core.deliverybatch')),
            ],
        ),
    ]
