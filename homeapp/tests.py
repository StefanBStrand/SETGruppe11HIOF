
# Create your tests here.

from unittest.mock import patch
import unittest

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.db import connection
from .models import SmartThermostat, CarCharger, SmartBulb, Home, Room
from django.test import Client



# Car charger stub tests

class CarChargerUnitTests(TestCase):
    def setUp(self):
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
        self.car_charger.is_connected_to_car = False
        self.car_charger.save()

        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertEqual(result, "No active charging session to stop.")
        self.assertFalse(self.car_charger.is_charging)

    def test_start_charging_with_zero_power_rate(self):
        # Simulate connection to car
        self.car_charger.is_connected_to_car = True
        self.car_charger.save()

        result = self.car_charger.start_charging(power_rate=0)
        self.assertFalse(self.car_charger.is_charging)
        self.assertEqual(result, "Cannot start charging with 0 kwh. Choose valid power rate")

    def test_connect_to_car(self):
        self.car_charger.is_connected_to_car = False
        self.car_charger.fetch_data()
        self.assertTrue(self.car_charger.is_connected_to_car)


    def test_start_charging(self):
        self.car_charger.is_connected_to_car = True
        self.car_charger.save()

        result = self.car_charger.start_charging(power_rate=10)
        self.assertTrue(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.power_consumption, 10)
        self.assertEqual(result, "Charging started at 10 kW.")

        result = self.car_charger.start_charging(power_rate=70)
        self.assertEqual(result, "Power rate exceeds maximum output capacity.")

    def test_stop_charging(self):
        self.car_charger.is_connected_to_car = True
        self.car_charger.is_charging = True
        self.car_charger.power_consumption = 10
        self.car_charger.save()

        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertFalse(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.total_power_consumption, 10)
        self.assertEqual(result, "Charging stopped. Total power consumed: 10.00 kWh.")

        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertEqual(result, "No active charging session to stop.")

    def test_reset_power_consumption(self):
        self.car_charger.total_power_consumption = 50
        result = self.car_charger.reset_power_consumption()
        self.assertEqual(self.car_charger.total_power_consumption, 0)
        self.assertEqual(result, "Total power consumption has been reset.")

    def test_calculate_estimated_charging_time_in_minutes(self):
        self.car_charger.is_connected_to_car = True
        self.car_charger.is_charging = True
        self.car_charger.power_consumption = 10
        self.car_charger.car_battery_charge = 10
        self.car_charger.save()

        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Estimated charging time: 102.00 minutes.")
        self.car_charger.car_battery_charge = 100
        self.car_charger.save()
        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Battery is already fully charged.")



#Smartbulb API stub tests

class SmartBulbUnitTests(TestCase):
    def setUp(self):
        self.smart_bulb = SmartBulb.objects.create(
            device_type="Smart Bulb",
            name="Living Room Bulb",
            brightness=100,
            color="white",
            is_on=False,
        )

    def test_fetch_data(self):
        data = self.smart_bulb.fetch_data()
        self.assertTrue(self.smart_bulb.is_on)
        self.assertEqual(self.smart_bulb.brightness, 75)
        self.assertEqual(self.smart_bulb.color, "blue")
        self.assertEqual(data["brightness"], 75)
        self.assertEqual(data["color"], "blue")

    def test_update_brightness(self):
        result = self.smart_bulb.update_brightness(50)
        self.assertEqual(self.smart_bulb.brightness, 50)
        self.assertEqual(result, "Brightness updated to 50%.")

    def test_invalid_brightness_low(self):
        result = self.smart_bulb.update_brightness(-10)
        self.assertEqual(result, "Invalid brightness value. Must be between 0 and 100.")
        self.assertEqual(self.smart_bulb.brightness, 100)

    def test_invalid_brightness_high(self):
        result = self.smart_bulb.update_brightness(150)
        self.assertEqual(result, "Invalid brightness value. Must be between 0 and 100.")
        self.assertEqual(self.smart_bulb.brightness, 100)

    def test_update_color(self):
        result = self.smart_bulb.update_color("red")
        self.assertEqual(self.smart_bulb.color, "red")
        self.assertEqual(result, "Color updated to red.")

    def test_invalid_color(self):
        result = self.smart_bulb.update_color("purple")
        self.assertEqual(result, "Invalid color value. Must be one of: white, black, red, green, yellow, blue.")
        self.assertEqual(self.smart_bulb.color, "white")  # Color should remain unchanged

    def test_turn_on(self):
        result = self.smart_bulb.turn_on()
        self.assertTrue(self.smart_bulb.is_on)
        self.assertEqual(result, "SmartBulb is now ON.")

    def test_turn_off(self):
        self.smart_bulb.turn_on()
        result = self.smart_bulb.turn_off()
        self.assertFalse(self.smart_bulb.is_on)
        self.assertEqual(result, "SmartBulb is now OFF.")


#Themorstat stub tests

class SmartThermostatTest(TestCase):
    def setUp(self):
        self.thermostat = SmartThermostat.objects.create(
            temperature_in_room=20,
            device_type = 'smartthermostat',
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


#Views tests
"""
class CreateSmartThermostatViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testbruker", password="testpassword")

    #Bruker ikke logget inn
    def test_create_thermostat_unauthenticated(self):
        response = self.client.get(reverse('new_device', args=['smartthermostat']))
        self.assertEqual(response.status_code, 302)

    #Bruker logget inn
    def test_create_thermostat_authenticated(self):
        self.client.login(username="testbruker", password="testpassword")
        response = self.client.post(reverse('new_device', args=['smartthermostat']), {
            'name': 'Test',
            'set_temperature': 22,
            'room': "",
            'mode': 'off',
            'device_type': 'smartthermostat',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SmartThermostat.objects.filter(name="Test").exists())

    def test_create_smartthermostat_invalid_data(self):
        self.client.login(username="testbruker", password="testpassword")

        response = self.client.post(reverse('new_device', args=['smartthermostat']), {
            'name': '',
            'set_temperature': 22,
            'room': '',
        })
        #FEil håndters i form
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SmartThermostat.objects.filter(set_temperature=22).exists())

class UpdateThermostatViewTests(TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.thermostat = SmartThermostat.objects.create(name="TestThermostat", owner=self.user, set_temperature=22,mode="off", device_type='smartthermostat')

    def test_update_thermostat(self):
        self.client.login(username="testbruker", password="testpassword")
        response = self.client.post(reverse('update_device', args=[self.thermostat.device_type, self.thermostat.id]), {
            'mode': 'cool'
        })
        self.assertEqual(response.status_code, 302)
        self.thermostat.refresh_from_db()
        self.assertEqual(self.thermostat.mode, 'cool')
"""

class ViewsTestings(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="TestBrukern", password="TestPassord")

        self.home = Home.objects.create(name="Hjem", owner=self.user)

        self.room = Room.objects.create(name="Stue", home=self.home)

        self.thermostat = SmartThermostat.objects.create(
            name="Thermostat i Stue",
            owner=self.user,
            room=self.room,
            set_temperature=22,
            mode="off",
            device_type="smartthermostat",
        )

        self.smartbulb = SmartBulb.objects.create(
            name="TestPæra",
            owner=self.user,
            room=self.room,
            is_on=False,
            device_type="smartbulb",
        )

        self.carcharger = CarCharger.objects.create(
            name="Billader",
            owner=self.user,
            room=self.room, #Vet det er rart med lader i stua ... :)
            is_connected_to_car=False,
            is_charging=False,
            device_type="carcharger",
        )

    def test_home_view_authenticated(self):
        self.client.login(username="TestBrukern", password="TestPassord")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thermostat i Stue")

    def test_home_view_unauthenticated(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)