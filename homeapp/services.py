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