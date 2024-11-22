from django.contrib import admin

# Register your models here.
from .models import Home, Room, CarCharger, SmartDevice, SmartThermostat, SmartBulb

class HomeAdmin(admin.ModelAdmin):
    exclude = ('lat', 'lon')


admin.site.register(Home, HomeAdmin)
admin.site.register(Room)
admin.site.register(CarCharger)
admin.site.register(SmartDevice)
admin.site.register(SmartThermostat)
admin.site.register(SmartBulb)