# Generated by Django 5.0.6 on 2024-05-29 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_proofofdelivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverybatch',
            name='delivered',
            field=models.BooleanField(default=False),
        ),
    ]
