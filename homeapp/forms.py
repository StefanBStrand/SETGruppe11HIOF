from django import forms
from .models import SmartThermostat, SmartBulb

class SmartThermostatForm(forms.ModelForm):
    class Meta:
        model = SmartThermostat
        fields = ['name', 'set_temperature', 'room']

        labels = {
            "name": "Navn på enhet",
            "room": "Rom enheten skal være i",
            "set_temperature": "Ønsket temperatur",
        }
