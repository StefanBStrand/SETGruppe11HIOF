# Generated by Django 5.1.1 on 2024-11-13 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0005_home_city_alter_smartbulb_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='home',
            name='lat',
            field=models.FloatField(default=59.21),
        ),
        migrations.AddField(
            model_name='home',
            name='lon',
            field=models.FloatField(default=10.92),
        ),
    ]
