# Generated by Django 5.0.3 on 2024-03-12 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_contact_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crate',
            name='id',
        ),
        migrations.AddField(
            model_name='crate',
            name='crate_id',
            field=models.CharField(default=1, max_length=50, primary_key=True, serialize=False, unique=True),
            preserve_default=False,
        ),
    ]
