import requests


def fetch_weather_data(lat, lon):
    # Henter værdata fra met.no sin API
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    # Legger til en header for å identifisere hvem som gjør forespørselen
    headers = {
        "User-Agent": "EasyHome sebhan@hiof.no"
    }
    params = {
        "lat": lat,
        "lon": lon
    }

    response = requests.get(url, headers=headers, params=params)


    if response.status_code == 200:
        data = response.json()
        try:
            air_temperature = data['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']
            humidity = data['properties']['timeseries'][0]['data']['instant']['details']['relative_humidity']
            wind = data['properties']['timeseries'][0]['data']['instant']['details']['wind_speed']
            return air_temperature, humidity, wind

        except KeyError:
            # Hvis vi ikke får tak i dataen vi trenger, returnerer vi None
            return None
    else:
        return None  # Eller håndter feil på en annen måte

    ####Stub functions####

    # stub APi functions car charger

def fetch_carcharger_data_from_external_system():
    # Simulates fetching car charger data from an external system.
    # Returns a successful response with simulated data.
    return {
        "response": "success",
        "car_battery_capacity": 40,
        "car_battery_charge": 25,
        "is_connected_to_car": True,  # Simulate connection status
        "is_charging": False,  # Simulate charging status
    }

def send_charging_status_to_external_system(power_rate, start=True):
    # Simulates sending a start/stop charging command to an external system.
    # Returns a successful response.
    return {
        "response": "success",
        "power_rate": power_rate,
        "action": "start" if start else "stop",
    }

# stub API functions smartbulb

def fetch_smartbulb_data_from_external_system():
    # Simulates fetching SmartBulb data from an external system.
    return {
        "is_on": True,
        "brightness": 75,
        "color": "blue",
    }

def send_brightness_update_to_external_system(new_brightness):
    # Simulates sending a brightness update to an external system.
    return {
        "response": "success",
        "updated_brightness": new_brightness,
    }

def send_color_update_to_external_system(new_color):
    # Simulates sending a color update to an external system.
    return {
        "response": "success",
        "updated_color": new_color,
    }

def send_turn_on_to_external_system():
    # Simulates sending a turn-on command to an external system.
    return {
        "response": "success",
    }

def send_turn_off_to_external_system():
    # Simulates sending a turn-off command to an external system.
    return {
        "response": "success",
    }

# stub API functions thermostat

def fetch_thermostat_data_from_external_system():

    # faste verdier som simulerer en typisk respons fra det eksterne systemet.
    return {
        "current_temperature": 21.5,
        "set_temperature": 22.0,
        "humidity": 45,
        "mode": "heat",
    }

def send_temperature_update_to_external_system(new_temperature):

    # faste verdier som simulerer en typisk respons fra det eksterne systemet.
    return {
        "response": "success",
        "updated_temperature": new_temperature
    }

def send_mode_update_to_external_system(new_mode):

    # faste verdier som simulerer en typisk respons fra det eksterne systemet.
    return {
        "response": "success",
        "updated_mode": new_mode
    }