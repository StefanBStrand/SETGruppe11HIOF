from django.contrib import admin

# Register your models here.
from .models import Home, Room, CarCharger, SmartDevice, SmartThermostat, SmartBulb

admin.site.register(Home)
admin.site.register(Room)
admin.site.register(CarCharger)
admin.site.register(SmartDevice)
admin.site.register(SmartThermostat)
admin.site.register(SmartBulb)