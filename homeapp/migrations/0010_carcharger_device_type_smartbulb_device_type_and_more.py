# Generated by Django 5.1.1 on 2024-11-14 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0009_alter_smartthermostat_set_temperature'),
    ]

    operations = [
        migrations.AddField(
            model_name='carcharger',
            name='device_type',
            field=models.CharField(default='carcharger', editable=False, max_length=50),
        ),
        migrations.AddField(
            model_name='smartbulb',
            name='device_type',
            field=models.CharField(default='smartbulb', editable=False, max_length=50),
        ),
        migrations.AddField(
            model_name='smartthermostat',
            name='device_type',
            field=models.CharField(default='smartthermostat', editable=False, max_length=50),
        ),
    ]
