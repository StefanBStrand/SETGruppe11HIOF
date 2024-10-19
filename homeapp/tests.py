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

    @patch('homeapp.views.update_thermostat')  # Use the correct app name 'homeapp'
    def test_update_thermostat_with_stub(self, mock_stub):
        # Mock the return value of the stub
        mock_stub.return_value = JsonResponse({
            'status': 'updated',
            'new_temperature': 22,
            'new_mode': 'cool'
        })

        # Test the logic that uses the stub
        url = reverse('update_thermostat', args=[self.thermostat.id])  # Use the created thermostat's ID
        response = self.client.post(url, {'mode': 'cool'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'status': 'updated',
            'new_temperature': 22,
            'new_mode': 'cool'
        })


class SmartThermostatUnitTest(TestCase):
    def setUp(self):
        self.thermostat = SmartThermostat.objects.create(
            temperature_in_room=20,
            set_temperature=22,
            humidity=45,
            mode='off'
        )

    def test_update_thermostat_mode_unit(self):
        url = reverse('update_thermostat', args=[self.thermostat.id])
        response = self.client.post(url, {'mode': 'cool'})
        self.thermostat.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.thermostat.mode, 'cool')
        self.assertJSONEqual(response.content, {
            'status': 'updated',
            'new_temperature': self.thermostat.set_temperature,
            'new_mode': 'cool'
        })
