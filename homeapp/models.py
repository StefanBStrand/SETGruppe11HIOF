from django.db import models
# Create your models here.


class Home(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Room(models.Model):
    name = models.CharField(max_length=128, unique=False)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class SmartDevice(models.Model):
    name = models.CharField(max_length=128)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CarCharger(SmartDevice):
    car_battery_capacity = models.IntegerField()
    car_battery_charge = models.IntegerField()
    is_connected_to_car = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    max_power_output = models.IntegerField()
    power_consumption = models.IntegerField(default=0)
    total_power_consumption = models.IntegerField(default=0)


class SmartBulb(SmartDevice):
    brightness = models.IntegerField(default=100)
    color = models.CharField(max_length=20, default='white')


class SmartThermostat(SmartDevice):
    temperature_in_room = models.IntegerField()
    set_temperature = models.IntegerField(default=22)  # TODO Change field to current_temperature.
    humidity = models.IntegerField()

    # Adding a mode field with possible choices
    MODE_CHOICES = [
        ('cool', 'Cooling'),
        ('heat', 'Heating'),
        ('off', 'Off'),
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='off')

    def get_temperature(self):
        return self.temperature_in_room

    def update_temperature(self, temperature):
        self.set_temperature = temperature

