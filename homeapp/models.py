from django.db import models
from services import *
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
    car_battery_capacity = models.IntegerField(default=40)
    car_battery_charge = models.IntegerField(default=0)
    is_connected_to_car = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    max_power_output = models.IntegerField(default=60)
    power_consumption = models.IntegerField(default=0)
    total_power_consumption = models.IntegerField(default=0)

    def fetch_data(self):
        # Fetches car charger data from a stub simulating the external system.
        # Updates local status if a change is detected.
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
        # Sends a start charging command to the external system.
        # Updates local charging status on success.
        if not self.is_connected_to_car:
            return "Car is not connected. Cannot start charging."
        
        if power_rate == 0:
            return "Cannot start charging with 0 kwh. Choose valid power rate"

        response = send_charging_status_to_external_system(power_rate, start=True)
        if response["response"] == "success":
            self.power_consumption = power_rate  # Update local power consumption
            self.is_charging = True  # Mark as charging
            self.save()
            return f"Charging started at {power_rate} kW."
        return "Failed to start charging."

    def stop_charging(self, charging_minutes):
        # Sends a stop charging command to the external system.
        # Updates local charging status on success.
        if not self.is_connected_to_car or not self.is_charging:
            return "No active charging session to stop."

        response = send_charging_status_to_external_system(0, start=False)
        if response["response"] == "success":
            # Calculate total power consumed during the charging session
            total_consumed = self.power_consumption * charging_minutes / 60
            self.total_power_consumption += total_consumed  # Update total power consumption
            self.power_consumption = 0  # Reset current power consumption
            self.is_charging = False  # Mark as not charging
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

    # Getters
    def get_battery_capacity(self):
        # Returns the total battery capacity of the car.
        return self.car_battery_capacity

    def get_battery_charge(self):
        # Returns the current charge level of the car battery.
        return self.car_battery_charge

    def get_is_connected_status(self):
        # Returns whether the car is connected to the charger.
        return self.is_connected_to_car

    def get_is_charging_status(self):
        # Returns whether the charger is actively charging.
        return self.is_charging

    def get_max_power_output(self):
        # Returns the maximum power output of the charger.
        return self.max_power_output

    def get_current_power_consumption(self):
        # Returns the current power consumption rate during charging.
        return self.power_consumption

    def get_total_power_consumption(self):
        # Returns the total power consumption of the charger.
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

    def fetch_data(self):
        # Fetches SmartBulb data from a stub simulating the external system.
        data = fetch_smartbulb_data_from_external_system()
        if data:
            self.is_on = data["is_on"]
            self.brightness = data["brightness"]
            self.color = data["color"]
            self.save()
        return data

    def update_brightness(self, new_brightness):
        # Checks if the new brightness value is valid
        if not (0 <= new_brightness <= 100):
            return "Invalid brightness value. Must be between 0 and 100."
        
        # Updates the brightness of the SmartBulb via a stub simulating the external system.
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
        
        # Updates the color of the SmartBulb via a stub simulating the external system.
        response = send_color_update_to_external_system(new_color)
        if response["response"] == "success":
            self.color = response["updated_color"]
            self.save()
            return f"Color updated to {self.color}."
        return "Failed to update color."

    def turn_on(self):
        # Turns on the SmartBulb via a stub simulating the external system.
        response = send_turn_on_to_external_system()
        if response["response"] == "success":
            self.is_on = True
            self.save()
            return "SmartBulb is now ON."
        return "Failed to turn on the SmartBulb."

    def turn_off(self):
        # Turns off the SmartBulb via a stub simulating the external system.
        response = send_turn_off_to_external_system()
        if response["response"] == "success":
            self.is_on = False
            self.save()
            return "SmartBulb is now OFF."
        return "Failed to turn off the SmartBulb."
    
    # Getters
    def get_brightness(self):
        # Returns the current brightness level
        return self.brightness

    def get_color(self):
        # Returns the current color of the SmartBulb
        return self.color

    def get_is_on_status(self):
        # Returns whether the SmartBulb is currently on
        return self.is_on


class SmartThermostat(SmartDevice):
    temperature_in_room = models.IntegerField()
    set_temperature = models.IntegerField(default=22)  
    humidity = models.IntegerField()

    # Adding a mode field with possible choices
    MODE_CHOICES = [
        ('cool', 'Cooling'),
        ('heat', 'Heating'),
        ('off', 'Off'),
    ]
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='off')

    def fetch_data(self):
        
        # Fetches thermostat data from a stub simulating the external system. Could run at intervals and look for changes.
        
        data = fetch_thermostat_data_from_external_system()
        if data:
            self.temperature_in_room = data["current_temperature"]
            self.set_temperature = data["set_temperature"]
            self.humidity = data["humidity"]
            self.mode = data["mode"]
            self.save()
        return data

    def update_temperature(self, new_temperature):
        
        # Updates the thermostat's temperature via a stub simulating the external system.
        
        response = send_temperature_update_to_external_system(new_temperature)
        if response["response"] == "success":
            self.set_temperature = response["updated_temperature"]
            self.save()
            return f"Temperature updated to {self.set_temperature}°C."
        return "Failed to update temperature."

    def update_mode(self, new_mode):
        
        # Updates the thermostat's mode via a stub simulating the external system.
        
        response = send_mode_update_to_external_system(new_mode)
        if response["response"] == "success":
            self.mode = response["updated_mode"]
            self.save()
            return f"Mode updated to {self.mode}."
        return "Failed to update mode."

    def get_temperature(self):
        # Returns the current room temperature
        return self.temperature_in_room

    def get_set_temperature(self):
        # Returns the desired temperature (set point)
        return self.set_temperature

    def get_humidity(self):
        # Returns the current humidity level
        return self.humidity

    def get_mode(self):
        # Returns the current operating mode of the thermostat
        return self.mode




        
    # Send request to Mock-api --> api.update_temperature()
    # Mock-apiet returnerer True/false basert på om det har gått ok.
    # Denne metoden returnerer denne true/false videre tilbake til controller (view)


    # TODO: method for view humidity
    # TODO: method for update mode.
    # TODO: method for view mode.
    # TODO: Teller positivt med lagring i db - funksjonene (SmartThermostat) må snakke med djangoDB.


    #TODO: Trykk på knapp i interfacet for å sette ny temperatur --> Kaller på funksjon i Controller (View)
    # --> Som igjen kaller på update_temperature-metode i Model