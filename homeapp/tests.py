
# Create your tests here.

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from .models import SmartThermostat


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
