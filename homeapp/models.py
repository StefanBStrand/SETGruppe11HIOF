from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .services import *


# Create your models here.


class Home(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    CITY_CHOICES = [
        ('Fredrikstad', 'Fredrikstad'),
        ('Sarpsborg', 'Sarpsborg'),
        ('Nesodden', 'Nesodden'), ]
    city = models.CharField(max_length=128, choices=CITY_CHOICES, blank=False, default='Fredrikstad')
    lat = models.FloatField(default=59.21)
    lon = models.FloatField(default=10.92)

    if city == 'Fredrikstad':
        lat = 59.21
        lon = 10.92
    elif city == 'Sarpsborg':
        lat = 59.28
        lon = 11.11
    elif city == 'Nesodden':
        lat = 59.84
        lon = 10.58

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=128, unique=False)
    home = models.ForeignKey(Home, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class SmartDevice(models.Model):
    device_type = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=128)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CarCharger(SmartDevice):
    car_battery_capacity = models.IntegerField(default=40)
    car_battery_charge = models.IntegerField(default=0)
    is_connected_to_car = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    max_power_output = models.IntegerField(default=60)
    power_consumption = models.IntegerField(default=0)
    total_power_consumption = models.IntegerField(default=0)
    device_type = 'carcharger'

    def fetch_data(self):
        data = fetch_carcharger_data_from_external_system()
        if data["response"] == "success":
            if data["is_connected_to_car"] != self.is_connected_to_car:
                self.is_connected_to_car = data["is_connected_to_car"]
            self.car_battery_capacity = data["car_battery_capacity"]
            self.car_battery_charge = data["car_battery_charge"]
            self.is_charging = data["is_charging"]
            self.save()
            return "Data fetched and local status updated successfully."
        return "Failed to fetch data from the external system."

    def start_charging(self, power_rate):
        if not self.is_connected_to_car:
            return "Car is not connected. Cannot start charging."

        if power_rate == 0:
            return "Cannot start charging with 0 kwh. Choose valid power rate"

        if power_rate > self.max_power_output:
            return "Power rate exceeds maximum output capacity."

        response = send_charging_status_to_external_system(power_rate, start=True)
        if response["response"] == "success":
            self.power_consumption = power_rate
            self.is_charging = True
            self.is_connected_to_car = True
            self.save()
            return f"Charging started at {power_rate} kW."
        return "Failed to start charging."

    def stop_charging(self, charging_minutes):
        if not self.is_connected_to_car or not self.is_charging:
            return "No active charging session to stop."

        response = send_charging_status_to_external_system(0, start=False)
        if response["response"] == "success":
            total_consumed = self.power_consumption * charging_minutes / 60
            self.total_power_consumption += total_consumed
            self.power_consumption = 0
            self.is_charging = False
            self.save()
            return f"Charging stopped. Total power consumed: {total_consumed:.2f} kWh."
        return "Failed to stop charging."

    def reset_power_consumption(self):

        self.total_power_consumption = 0
        self.save()
        return "Total power consumption has been reset."

    def calculate_estimated_charging_time_in_minutes(self):
        if not self.is_connected_to_car:
            return "Car is not connected."

        if not self.is_charging or self.power_consumption <= 0:
            return "No active charging session."

        remaining_capacity = self.car_battery_capacity - self.car_battery_charge
        if remaining_capacity <= 0:
            return "Battery is already fully charged."

        charging_time_minutes_to_full = (remaining_capacity / (self.power_consumption)) * 60
        return "Estimated charging time: {:.2f} minutes.".format(charging_time_minutes_to_full)


    def get_device_type(self):
        return "carcharger"

    def get_battery_capacity(self):
        return self.car_battery_capacity

    def get_battery_charge(self):
        return self.car_battery_charge

    def get_is_connected_status(self):
        return self.is_connected_to_car

    def get_is_charging_status(self):
        return self.is_charging

    def get_max_power_output(self):
        return self.max_power_output

    def get_current_power_consumption(self):
        return self.power_consumption

    def get_total_power_consumption(self):
        return self.total_power_consumption


class SmartBulb(SmartDevice):
    COLOR_CHOICES = [
        ('white', 'White'),
        ('black', 'Black'),
        ('red', 'Red'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('blue', 'Blue'),
    ]

    brightness = models.IntegerField(default=100)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white')
    device_type = 'smartbulb'

    def fetch_data(self):
        data = fetch_smartbulb_data_from_external_system()
        if data:
            self.is_on = data["is_on"]
            self.brightness = data["brightness"]
            self.color = data["color"]
            self.save()
        return data

    def update_brightness(self, new_brightness):
        if not (0 <= new_brightness <= 100):
            return "Invalid brightness value. Must be between 0 and 100."

        response = send_brightness_update_to_external_system(new_brightness)
        if response["response"] == "success":
            self.brightness = response["updated_brightness"]
            self.save()
            return f"Brightness updated to {self.brightness}%."
        return "Failed to update brightness."

    def update_color(self, new_color):
        if new_color not in dict(self.COLOR_CHOICES):
            return f"Invalid color value. Must be one of: {', '.join(dict(self.COLOR_CHOICES).keys())}."

        response = send_color_update_to_external_system(new_color)
        if response["response"] == "success":
            self.color = response["updated_color"]
            self.save()
            return f"Color updated to {self.color}."
        return "Failed to update color."

    def turn_on(self):
        response = send_turn_on_to_external_system()
        if response["response"] == "success":
            self.is_on = True
            self.save()
            return "SmartBulb is now ON."
        return "Failed to turn on the SmartBulb."

    def turn_off(self):
        response = send_turn_off_to_external_system()
        if response["response"] == "success":
            self.is_on = False
            self.save()
            return "SmartBulb is now OFF."
        return "Failed to turn off the SmartBulb."

    def get_device_type(self):
        return "smartbulb"

    def get_brightness(self):
        return self.brightness

    def get_color(self):
        return self.color

    def get_is_on_status(self):
        return self.is_on


class SmartThermostat(SmartDevice):
    temperature_in_room = models.IntegerField(blank=True, null=True, default=22, validators=[MinValueValidator(5),
        MaxValueValidator(30)])
    set_temperature = models.IntegerField(default=22, validators=[MinValueValidator(5), MaxValueValidator(30)])
    humidity = models.IntegerField(blank=True, null=True, default=45)
    device_type = 'smartthermostat'

    MODE_CHOICES = [
        ('cool', 'Cooling'),
        ('heat', 'Heating'),
        ('off', 'Off'),
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='off')

    def fetch_data(self):

        data = fetch_thermostat_data_from_external_system()
        if data:
            self.temperature_in_room = data["current_temperature"]
            self.set_temperature = data["set_temperature"]
            self.humidity = data["humidity"]
            self.mode = data["mode"]
            self.save()
        return data

    def update_temperature(self, new_temperature):
        if new_temperature < 5 or new_temperature > 30:
            return "Temperatur må være mellom 5 og 30 grader."
        response = send_temperature_update_to_external_system(new_temperature)
        if response["response"] == "success":
            self.set_temperature = response["updated_temperature"]
            #self.temperature_in_room = new_temperature (Kommentert ut: Var før satt til temp med en gang.)
            self.save()
            if self.set_temperature > self.temperature_in_room:
                self.update_mode('heat')
            elif self.set_temperature < self.temperature_in_room:
                self.update_mode('cool')
            else:
                self.update_mode('off')
            return f"Temperatur oppdatert til {self.set_temperature}°C."
        return "Feil ved oppdatering i av temperatur."

    def update_mode(self, new_mode):

        response = send_mode_update_to_external_system(new_mode)
        if response["response"] == "success":
            self.mode = response["updated_mode"]
            self.save()
            return f"Modus oppdatert til {self.mode}."
        return "Feil ved oppdatering av modus."

    def get_temperature(self):
        return self.temperature_in_room

    def get_set_temperature(self):
        return self.set_temperature

    def get_humidity(self):
        return self.humidity

    def get_mode(self):
        return self.mode

    def get_device_type(self):
        return "smartthermostat"

