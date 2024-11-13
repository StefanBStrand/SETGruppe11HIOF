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
    car_battery_capacity = models.IntegerField(default=40)
    car_battery_charge = models.IntegerField(default=0)
    is_connected_to_car = models.BooleanField(default=False)
    is_charging = models.BooleanField(default=False)
    max_power_output = models.IntegerField(default=60)
    power_consumption = models.IntegerField(default=0)
    total_power_consumption = models.IntegerField(default=0)

    def connect_to_car(self):
        if not self.is_connected_to_car:
            self.is_connected_to_car = True
            self.save()
            return "Car is now connected."
        return "Car is already connected."

    def disconnect_from_car(self):
        if self.is_connected_to_car:
            self.is_connected_to_car = False
            self.save()
            return "Car is now disconnected."
        return "Car is already disconnected."

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


class SmartBulb(SmartDevice):
    COLOR_CHOICES = [
        ('white', 'White'),
        ('black', 'Black'),
        ('red', 'Red'),
        ('green', 'Green'),
        ('yellow', 'Yellow')
    ]

    brightness = models.IntegerField(default=100)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='white')


    def turn_on(self):
        """Skrur på lyset"""
        self.is_on = True
        print("Turning on.")

    def turn_off(self):
        self.is_on = False
        print("Turning off.")

    def set_brightness(self, value):
        if 0 <= value <= 100:
            self.brightness = value
            print(f"Brightness set to {value}%.")

    def set_color(self, new_color):
        if new_color in dict(self.COLOR_CHOICES):
            self.color = new_color
            print(f"Color set to {new_color}.")

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
        # Send request to Mock-api --> api.update_temperature()
        # Mock-apiet returnerer True/false basert på om det har gått ok.
        # Denne metoden returnerer denne true/false videre tilbake til controller (view)


    # TODO: method for view humidity
    # TODO: method for update mode.
    # TODO: method for view mode.
    # TODO: Teller positivt med lagring i db - funksjonene (SmartThermostat) må snakke med djangoDB.


    #TODO: Trykk på knapp i interfacet for å sette ny temperatur --> Kaller på funksjon i Controller (View)
    # --> Som igjen kaller på update_temperature-metode i Model