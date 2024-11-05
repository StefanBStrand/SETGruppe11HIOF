
# Create your tests here.

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from .models import SmartThermostat, CarCharger, SmartBulb


class SmartThermostatViewTest(TestCase):

    def setUp(self):
        # Create a SmartThermostat instance for testing
        self.thermostat = SmartThermostat.objects.create(
            temperature_in_room=20,
            set_temperature=22,
            humidity=45,
            mode='off'
        )

    def test_update_thermostat_view_valid(self):
        # Test a valid POST request to update the thermostat
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'cool'})
        self.thermostat.refresh_from_db()

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(self.thermostat.mode, 'cool')
        self.assertRedirects(response, reverse('thermostat_view', args=[self.thermostat.id]))

    def test_update_thermostat_view_invalid_mode(self):
        # Test an invalid mode submission
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'invalid_mode'})
        self.thermostat.refresh_from_db()

        self.assertEqual(response.status_code, 200)  # Should not redirect, stay on the page
        self.assertNotEqual(self.thermostat.mode, 'invalid_mode')
        self.assertContains(response, "Invalid mode selected.")

    def test_update_thermostat_view_non_existent(self):
        # Test for a non-existent thermostat (404 response)
        non_existent_url = reverse('update_thermostat', args=[9999])  # Assume 9999 doesn't exist
        response = self.client.post(non_existent_url, {'mode': 'cool'})

        self.assertEqual(response.status_code, 404)

    def test_update_thermostat_redirect(self):
        # Test that a successful update behaves as expected with a redirect
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'heat'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('thermostat_view', args=[self.thermostat.id]))

    # Thermostat_detail tests: ******

    def test_thermostat_detail_view_exists(self):
        # Test that the detail view returns a 200 status code for an existing thermostat
        url = reverse('thermostat_view', args=[self.thermostat.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'thermostat_detail.html')
        self.assertContains(response, self.thermostat.set_temperature)
        self.assertContains(response, self.thermostat.mode)

    def test_thermostat_detail_view_non_existent(self):
        # Test that the detail view returns a 404 status code for a non-existent thermostat
        non_existent_url = reverse('thermostat_view', args=[9999])  # Assuming 9999 doesn't exist
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, 404)

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

class TestSmartBulbUnitTests(TestCase):
    def setUp(self):
        self.bulb = SmartBulb.objects.create(
            brightness=100,
            color='white',
            is_on=True
        )

    def test_turn_on(self):
        self.bulb.turn_off()

        self.bulb.turn_on()

        self.assertTrue(self.bulb.is_on)

    def test_turn_off(self):
        self.bulb.turn_off()

        self.assertFalse(self.bulb.is_on)

    def test_set_brightness_valid(self):
        self.bulb.set_brightness(65)

        self.assertEqual(self.bulb.brightness, 65)

    def test_set_brightness_invalid(self):
        self.bulb.set_brightness(150)

        self.assertNotEqual(self.bulb.brightness, 150)
        self.assertEqual(self.bulb.brightness, 100)

    def test_set_color_valid(self):
        self.bulb.set_color('blue')

        self.assertEqual(self.bulb.color, 'blue')

    def test_set_color_invalid(self):
        self.bulb.set_color('purple')

        self.assertNotEqual(self.bulb.color, 'purple')
        self.assertEqual(self.bulb.color, 'white')

    def test_toggle_on_and_off(self):
        self.bulb.turn_off()
        self.assertFalse(self.bulb.is_on)

        self.test_turn_on()
        self.assertTrue(self.bulb.is_on)
