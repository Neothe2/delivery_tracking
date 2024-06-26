# Generated by Django 5.0.4 on 2024-04-22 04:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_rename_contact_details_customer_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='core.customer')),
            ],
        ),
        migrations.AlterField(
            model_name='deliverybatch',
            name='delivery_address',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.address'),
        ),
    ]
