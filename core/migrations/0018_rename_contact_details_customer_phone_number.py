# Generated by Django 5.0.4 on 2024-04-17 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_remove_crate_contents'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='contact_details',
            new_name='phone_number',
        ),
    ]