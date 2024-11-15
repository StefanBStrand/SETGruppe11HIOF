
# Create your tests here.

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.db import connection
from .models import SmartBulb, SmartThermostat, CarCharger
from .services import *
from django.test import Client

# Car charger stub tests

class CarChargerUnitTests(TestCase):
    def setUp(self):
        # Create a CarCharger instance for testing
        self.car_charger = CarCharger.objects.create(
            device_type="Car Charger",
            car_battery_capacity=27,
            car_battery_charge=10,
            is_connected_to_car=False,
            is_charging=False,
            max_power_output=60,
            power_consumption=0,
            total_power_consumption=0,
        )

    def test_stop_charging_when_not_connected(self):
        # Test stopping charging when not connected to the car
        self.car_charger.is_connected_to_car = False
        self.car_charger.save()

        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertEqual(result, "No active charging session to stop.")
        self.assertFalse(self.car_charger.is_charging)

    def test_start_charging_with_zero_power_rate(self):
        # Simulate connection to car
        self.car_charger.is_connected_to_car = True
        self.car_charger.save()

        # Test starting charging with zero power rate
        result = self.car_charger.start_charging(power_rate=0)
        self.assertFalse(self.car_charger.is_charging)
        self.assertEqual(result, "Cannot start charging with 0 kwh. Choose valid power rate")

    def test_connect_to_car(self):
        # Test connecting to the car
        self.car_charger.is_connected_to_car = False
        self.car_charger.fetch_data()  # Simulate fetching data that changes connection status
        self.assertTrue(self.car_charger.is_connected_to_car)


    def test_start_charging(self):
        # Simulate connection to car
        self.car_charger.is_connected_to_car = True
        self.car_charger.save()

        # Test starting charging with valid power rate
        result = self.car_charger.start_charging(power_rate=10)
        self.assertTrue(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.power_consumption, 10)
        self.assertEqual(result, "Charging started at 10 kW.")

        # Test starting charging with power rate exceeding capacity
        result = self.car_charger.start_charging(power_rate=70)
        self.assertEqual(result, "Power rate exceeds maximum output capacity.")

    def test_stop_charging(self):
        # Simulate connection and active charging
        self.car_charger.is_connected_to_car = True
        self.car_charger.is_charging = True
        self.car_charger.power_consumption = 10
        self.car_charger.save()

        # Test stopping charging
        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertFalse(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.total_power_consumption, 10)  # 10 kW * 1 hour
        self.assertEqual(result, "Charging stopped. Total power consumed: 10.00 kWh.")

        # Test stopping charging when no active session
        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertEqual(result, "No active charging session to stop.")

    def test_reset_power_consumption(self):
        # Set total power consumption and test reset
        self.car_charger.total_power_consumption = 50
        result = self.car_charger.reset_power_consumption()
        self.assertEqual(self.car_charger.total_power_consumption, 0)
        self.assertEqual(result, "Total power consumption has been reset.")

    def test_calculate_estimated_charging_time_in_minutes(self):
        # Simulate connection and charging
        self.car_charger.is_connected_to_car = True
        self.car_charger.is_charging = True
        self.car_charger.power_consumption = 10
        self.car_charger.car_battery_charge = 10
        self.car_charger.save()

        # Test calculating time to full charge
        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Estimated charging time: 102.00 minutes.")

        # Test with battery fully charged
        self.car_charger.car_battery_charge = 100
        self.car_charger.save()
        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Battery is already fully charged.")



#Smartbulb API stub tests

class SmartBulbUnitTests(TestCase):
    def setUp(self):
        # Create a SmartBulb instance for testing
        self.smart_bulb = SmartBulb.objects.create(
            device_type="Smart Bulb",  # Added device_type
            name="Living Room Bulb",
            brightness=100,
            color="white",
            is_on=False,
        )

    def test_fetch_data(self):
        # Test fetching data from the stub
        data = self.smart_bulb.fetch_data()
        self.assertTrue(self.smart_bulb.is_on)
        self.assertEqual(self.smart_bulb.brightness, 75)
        self.assertEqual(self.smart_bulb.color, "blue")
        self.assertEqual(data["brightness"], 75)
        self.assertEqual(data["color"], "blue")

    def test_update_brightness(self):
        # Test updating the brightness with valid input
        result = self.smart_bulb.update_brightness(50)
        self.assertEqual(self.smart_bulb.brightness, 50)
        self.assertEqual(result, "Brightness updated to 50%.")

    def test_invalid_brightness_low(self):
        # Test updating the brightness with a value below 0
        result = self.smart_bulb.update_brightness(-10)
        self.assertEqual(result, "Invalid brightness value. Must be between 0 and 100.")
        self.assertEqual(self.smart_bulb.brightness, 100)  # Brightness should remain unchanged

    def test_invalid_brightness_high(self):
        # Test updating the brightness with a value above 100
        result = self.smart_bulb.update_brightness(150)
        self.assertEqual(result, "Invalid brightness value. Must be between 0 and 100.")
        self.assertEqual(self.smart_bulb.brightness, 100)  # Brightness should remain unchanged

    def test_update_color(self):
        # Test updating the color with valid input
        result = self.smart_bulb.update_color("red")
        self.assertEqual(self.smart_bulb.color, "red")
        self.assertEqual(result, "Color updated to red.")

    def test_invalid_color(self):
        # Test updating the color with an invalid value
        result = self.smart_bulb.update_color("purple")
        self.assertEqual(result, "Invalid color value. Must be one of: white, black, red, green, yellow, blue.")
        self.assertEqual(self.smart_bulb.color, "white")  # Color should remain unchanged

    def test_turn_on(self):
        # Test turning on the bulb
        result = self.smart_bulb.turn_on()
        self.assertTrue(self.smart_bulb.is_on)
        self.assertEqual(result, "SmartBulb is now ON.")

    def test_turn_off(self):
        # Test turning off the bulb
        self.smart_bulb.turn_on()  # Ensure it's ON first
        result = self.smart_bulb.turn_off()
        self.assertFalse(self.smart_bulb.is_on)
        self.assertEqual(result, "SmartBulb is now OFF.")


#Themorstat stub tests

class SmartThermostatTest(TestCase):
    def setUp(self):
        self.thermostat = SmartThermostat.objects.create(
            device_type="Thermostat",  # Added device_type
            temperature_in_room=20,
            set_temperature=22,
            humidity=45,
            mode='off'
        )

    def test_fetch_data(self):
        data = self.thermostat.fetch_data()
        self.assertEqual(data["current_temperature"], 21.5)
        self.assertEqual(data["set_temperature"], 22.0)
        self.assertEqual(data["humidity"], 45)
        self.assertEqual(data["mode"], "heat")
        self.assertEqual(self.thermostat.temperature_in_room, 21.5)
        self.assertEqual(self.thermostat.set_temperature, 22.0)
        self.assertEqual(self.thermostat.humidity, 45)
        self.assertEqual(self.thermostat.mode, "heat")


    def test_update_temperature(self):
        result = self.thermostat.update_temperature(24)
        self.assertEqual(self.thermostat.set_temperature, 24)
        self.assertEqual(result, "Temperature updated to 24°C.")

    def test_update_mode(self):
        result = self.thermostat.update_mode("cool")
        self.assertEqual(self.thermostat.mode, "cool")
        self.assertEqual(result, "Mode updated to cool.")


