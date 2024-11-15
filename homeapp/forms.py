from django import forms
from .models import SmartThermostat, SmartBulb, CarCharger


class SmartThermostatForm(forms.ModelForm):
    class Meta:
        model = SmartThermostat
        fields = ['name', 'set_temperature', 'room']

        labels = {
            "name": "Visningsnavn på termostat",
            "room": "Rom enheten skal være i",
            "set_temperature": "Ønsket temperatur",
        }

class SmartBulbForm(forms.ModelForm):
    class Meta:
        model = SmartBulb
        fields = ['is_on','name', 'color', 'room']

        labels = {
            "name": "Visningsnavn på smartpære",
            "room": "Rom enheten skal være i",
            "is_on": "Pære på",

        }

class CarChargerForm(forms.ModelForm):
    class Meta:
        model = CarCharger
        fields = ['name', 'room']

        labels = {
            "name": "Visningsnavn på lader",
            "room": "Rom enheten skal være i",

        }
