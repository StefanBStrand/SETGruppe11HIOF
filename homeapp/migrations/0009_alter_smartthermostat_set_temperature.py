# Generated by Django 5.1.1 on 2024-11-14 19:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0008_alter_smartthermostat_humidity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartthermostat',
            name='set_temperature',
            field=models.IntegerField(default=22, validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(30)]),
        ),
    ]