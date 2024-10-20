from django.test import TestCase

# Create your tests here.

from django.http import JsonResponse
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from .models import SmartThermostat


class SmartThermostatViewTest(TestCase):
    def setUp(self):
        # Create a SmartThermostat instance before each test
        self.thermostat = SmartThermostat.objects.create(
            temperature_in_room=20,
            set_temperature=22,
            humidity=45,
            mode='off'
        )

    def test_update_thermostat_view(self):
        # Test the POST request that updates the thermostat
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'cool'})
        self.thermostat.refresh_from_db()

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Ensure the correct template is used
        self.assertTemplateUsed(response, 'thermostat.html')

        # Check if the template contains the updated mode
        self.assertContains(response, 'updated')
        self.assertContains(response, 'cool')
        self.assertContains(response, '22')  # Check if temperature is displayed
