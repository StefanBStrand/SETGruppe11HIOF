# Generated by Django 5.1.1 on 2024-10-18 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0002_smartthermostat_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='smartthermostat',
            name='set_temperature',
            field=models.IntegerField(default=22),
        ),
    ]
