
# Create your tests here.

from unittest.mock import patch
import unittest
from django.test import TestCase
from django.urls import reverse
from django.db import connection
from .models import SmartThermostat, CarCharger
from django.test import Client


class SmartThermostatViewTest(unittest.TestCase):
    def setUp(self):
        # Set up the test client and manually initialize the database connection
        self.client = Client()
        self.thermostat = SmartThermostat.objects.create(
            temperature_in_room=20,
            set_temperature=22,
            humidity=45,
            mode='off'
        )

    def tearDown(self):
        # Clean up the database after each test, avoiding django automation.
        SmartThermostat.objects.all().delete()
        connection.close()

    def test_update_thermostat_view_valid(self):
        # Step 1: Define the URL and action
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'cool'})

        # Step 2: Refresh the thermostat instance from the database to reflect any updates
        self.thermostat.refresh_from_db()

        # Step 3: Assertions using core Python `assert`
        assert response.status_code == 302  # Check if the response indicates a redirect
        assert response['Location'] == reverse('thermostat_detail', args=[self.thermostat.id])  # Verify redirect URL
        assert self.thermostat.mode == 'cool'  # Ensure the mode was updated to 'cool'

    def test_update_thermostat_view_invalid_mode(self):
        # Step 1: Define the URL and action
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'invalid_mode'})

        # Step 2: Refresh the thermostat instance from the database
        self.thermostat.refresh_from_db()

        # Step 3: Assertions using core Python `assert`
        assert response.status_code == 200  # Check that the response does not redirect
        assert self.thermostat.mode != 'invalid_mode'  # Ensure the mode was not changed
        assert "Invalid mode selected." in response.content.decode()  # Check for error message in the response content

    def test_update_thermostat_view_non_existent(self):
        # Step 1: Define the URL for a non-existent thermostat ID
        non_existent_url = reverse('update_thermostat', args=[9999])  # Assume ID 9999 doesn't exist
        response = self.client.post(non_existent_url, {'mode': 'cool'})

        # Step 2: Assertions using core Python `assert`
        assert response.status_code == 404  # Check for 404 response indicating not found

    def test_update_thermostat_redirect(self):
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'heat'})

        assert response.status_code == 302  # Check for redirect
        assert response['Location'] == reverse('thermostat_detail', args=[self.thermostat.id])  # Correct redirect URL


    # Thermostat_detail tests: ******

    def test_thermostat_detail_view_exists(self):
        # Step 1: Define the URL and action
        url = reverse('thermostat_detail', args=[self.thermostat.id])
        response = self.client.get(url)

        # Step 2: Assertions using core Python `assert`
        assert response.status_code == 200  # Check for successful response
        assert 'thermostat_detail.html' in [t.name for t in response.templates]  # Confirm correct template is used
        assert str(self.thermostat.set_temperature) in response.content.decode()  # Check content for set temperature
        assert self.thermostat.mode in response.content.decode()  # Check content for current mode

    def test_thermostat_detail_view_non_existent(self):
        # Step 1: Define the URL for a non-existent thermostat ID
        non_existent_url = reverse('thermostat_detail', args=[9999])  # Assume ID 9999 doesn't exist
        response = self.client.get(non_existent_url)

        # Step 2: Assertions using core Python `assert`
        assert response.status_code == 404  # Check for 404 response indicating not found

    # ******* CarCharger Tests ********

class CarChargerUnitTests(TestCase):
    def setUp(self):
        self.car_charger = CarCharger.objects.create(
            car_battery_capacity=27,
            car_battery_charge=10,
            max_power_output=60,
            power_consumption=50,
            total_power_consumption=0
        )

    def test_connect_to_car(self):
        # Tester kobling til bilen
        result = self.car_charger.connect_to_car()
        self.assertTrue(self.car_charger.is_connected_to_car)
        self.assertEqual(result, "Car is now connected.")

        # Tester forsøk på tilkobling når bilen allerede er tilkoblet
        result = self.car_charger.connect_to_car()
        self.assertEqual(result, "Car is already connected.")

    def test_disconnect_from_car(self):
        # kobler til bilen
        self.car_charger.connect_to_car()

        # Tester frakobling av bilen
        result = self.car_charger.disconnect_from_car()
        self.assertFalse(self.car_charger.is_connected_to_car)
        self.assertEqual(result, "Car is now disconnected.")

        # Tester forsøk på frakobling når bilen allerede er frakoblet
        result = self.car_charger.disconnect_from_car()
        self.assertEqual(result, "Car is already disconnected.")

    def test_start_charging(self):
        # Kobler til bilen først
        self.car_charger.connect_to_car()

        # Starter lading med en gyldig effekt
        result = self.car_charger.start_charging(power_rate=10)
        self.assertTrue(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.power_consumption, 10)
        self.assertEqual(result, "Charging started at 10 kW.")

        # Starter lading med en effekt høyere enn maks kapasitet
        result = self.car_charger.start_charging(power_rate=25)
        self.assertEqual(result, "Power rate exceeds maximum output capacity.")


    def test_stop_charging(self):
        # Kobler til bilen og start lading først
        self.car_charger.connect_to_car()
        self.car_charger.start_charging(power_rate=10)

        # Stopper lading etter 60 minutter (1 time)
        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertFalse(self.car_charger.is_charging)
        self.assertEqual(self.car_charger.total_power_consumption, 10)  # 10 kW * 1 time
        self.assertEqual(result, "Charging stopped. Total power consumed: 10.00 kWh.")

        # Stopper lading når det ikke er en aktiv ladesesjon
        result = self.car_charger.stop_charging(charging_minutes=60)
        self.assertEqual(result, "No active charging session to stop.")

    def test_reset_power_consumption(self):
        # Setter totalt strømforbruk til en verdi
        self.car_charger.total_power_consumption = 50

        # Nullstiller strømforbruket
        result = self.car_charger.reset_power_consumption()
        self.assertEqual(self.car_charger.total_power_consumption, 0)
        self.assertEqual(result, "Total power consumption has been reset.")

    def test_calculate_estimated_charging_time_in_minutes(self):
        # Kobler til bilen og start lading først
        self.car_charger.connect_to_car()
        self.car_charger.start_charging(power_rate=10)

        # Estimerer ladetid fra nåværende lading til full kapasitet
        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Estimated charging time: 300.00 minutes.")

        # Setter batteriet til fulladet og verifiserer
        self.car_charger.car_battery_charge = 100
        self.car_charger.save()
        result = self.car_charger.calculate_estimated_charging_time_in_minutes()
        self.assertEqual(result, "Battery is already fully charged.")
