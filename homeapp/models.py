from django.db import models

# Create your models here.

class SmartDevice(models.Model):
    name = models.CharField(max_length=128)
   # room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CarCharger(SmartDevice):
    is_connected_to_car = models.BooleanField(default=False)
    power_consumption = models.IntegerField(default=0)
    total_power_consumption = models.IntegerField(default=0)

class SmartThermostat(SmartDevice):
    temperature_in_room = models.IntegerField()
    set_temperature = models.IntegerField()
    humidity = models.IntegerField()

    def get_temperature(self):
        #  Call stub to get a temp reading?
        return self.temperature_in_room

    def set_temperature(self, temperature):
        self.set_temperature = temperature