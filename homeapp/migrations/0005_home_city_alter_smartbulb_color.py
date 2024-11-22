# Generated by Django 5.1.1 on 2024-11-13 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0004_carcharger_car_battery_capacity_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='home',
            name='city',
            field=models.CharField(choices=[('Fredrikstad', 'Fredrikstad'), ('Sarpsborg', 'Sarpsborg'), ('Nesodden', 'Nesodden')], default='Fredrikstad', max_length=128),
        ),
        migrations.AlterField(
            model_name='smartbulb',
            name='color',
            field=models.CharField(choices=[('white', 'White'), ('black', 'Black'), ('red', 'Red'), ('green', 'Green'), ('yellow', 'Yellow')], default='white', max_length=20),
        ),
    ]
