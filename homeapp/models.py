from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from homeapp.services import send_turn_off_to_external_system, fetch_thermostat_data_from_external_system, \
    send_temperature_update_to_external_system, send_mode_update_to_external_system, send_turn_on_to_external_system


# Create your models here.


class Home(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=True)
    CITY_CHOICES = [
        ('Fredrikstad', 'Fredrikstad'),
        ('Sarpsborg', 'Sarpsborg'),
        ('Nesodden', 'Nesodden'),]
    city = models.CharField(max_length=128, choices=CITY_CHOICES ,blank=False, default='Fredrikstad')
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
        return f"{self.name}"


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
    device_type = models.CharField(max_length=50, default='smartdevice')

    def save(self, *args, **kwargs):
        # Bare sett device_type hvis det ikke allerede er satt
        if not self.device_type:
            self.device_type = self.DEVICE_TYPE  # Bruk konstanten fra underklassen
        super().save(*args, **kwargs)


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


    def get_device_type(self):
        return "carcharger"


    def fetch_data(self):

        data = fetch_carcharger_data_from_external_system()
        if data["response"] == "success":
            # Update connection status if changed
            if data["is_connected_to_car"] != self.is_connected_to_car:
                self.is_connected_to_car = data["is_connected_to_car"]

            # Update other fields based on the fetched data
            self.car_battery_capacity = data["car_battery_capacity"]
            self.car_battery_charge = data["car_battery_charge"]
            self.is_charging = data["is_charging"]
            self.save()
            return "Data fetched and local status updated successfully."
        return "Failed to fetch data from the external system."

    def start_charging(self, power_rate):

        if not self.is_connected_to_car:
            raise ValueError("Car is not connected. Please connect the car to start charging.")
        if power_rate <= self.max_power_output:
            self.power_consumption = power_rate
            self.is_charging = True
            self.save()
            return "Charging started at {} kW.".format(power_rate)

    def stop_charging(self, charging_minutes):

        if self.is_connected_to_car and self.power_consumption > 0 and self.is_charging:
            self.is_charging = False
            total_consumed = self.power_consumption * charging_minutes
            self.total_power_consumption += total_consumed
            self.power_consumption = 0
            self.save()
            return "Charging stopped. Total power consumed: {} kWh.".format(total_consumed)
        return "No active charging session to stop."

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

    def get_device_type(self):
        return "smartbulb"


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
        # Checks if the new color value is valid
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
    
    # Getters
    def get_brightness(self):
        return self.brightness

    def get_color(self):
        return self.color

    def get_is_on_status(self):
        return self.is_on


class SmartThermostat(SmartDevice):
    temperature_in_room = models.IntegerField(default=22)
    set_temperature = models.IntegerField(default=22)  
    humidity = models.IntegerField(default=50)

    def get_device_type(self):
        return "smartthermostat"

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
        
        response = send_temperature_update_to_external_system(new_temperature)
        if response["response"] == "success":
            self.set_temperature = response["updated_temperature"]
            self.save()
            return f"Temperature updated to {self.set_temperature}°C."
        return "Failed to update temperature."

    def update_mode(self, new_mode):
        
        response = send_mode_update_to_external_system(new_mode)
        if response["response"] == "success":
            self.mode = response["updated_mode"]
            self.save()
            return f"Mode updated to {self.mode}."
        return "Failed to update mode."

    def get_temperature(self):
        return self.temperature_in_room

    def get_set_temperature(self):
        return self.set_temperature

    def get_humidity(self):
        return self.humidity

    def get_mode(self):
        return self.mode




        
    # Send request to Mock-api --> api.update_temperature()
    # Mock-apiet returnerer True/false basert på om det har gått ok.
    # Denne metoden returnerer denne true/false videre tilbake til controller (view)


