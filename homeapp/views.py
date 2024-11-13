from .forms import SmartThermostatForm
# Create your views here.
from .models import Home, Room, SmartDevice, CarCharger, SmartThermostat
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy



from django.contrib.auth.decorators import login_required

from .services import fetch_weather_data


@login_required(login_url='/accounts/login/')
def home_view(request):
    user = request.user

    home = Home.objects.filter(owner=user).first()
    lon = home.lon
    lat = home.lat
    air_temperature, humidity, wind = fetch_weather_data(lat, lon)

    context = {
        'user': user,
        'home': home,
        'rooms': Room.objects.filter(home__owner=user),
        'devices': SmartDevice.objects.filter(owner=user),
        'chargers': CarCharger.objects.filter(owner=user),
        'air_temperature': air_temperature,
        'humidity': humidity,
        'wind': wind,
    }
    return render(request, 'home.html', context)

@login_required
def create_smart_thermostat_device_view(request):
    if request.method == 'POST':
        form = SmartThermostatForm(request.POST)
        if form.is_valid():
            smart_thermostat = form.save(commit=False)
            smart_thermostat.owner = request.user  # Setter eieren til innlogget bruker
            smart_thermostat.save()
            return redirect(reverse_lazy('home'))
    else:
        form = SmartThermostatForm()

    return render(request, 'create_device.html', {'form': form})

def update_thermostat(request, id):
    # Fetch the thermostat object or return a 404 page if it doesn't exist
    thermostat = get_object_or_404(SmartThermostat, id=id)

    if request.method == "POST":
        mode = request.POST.get('mode')

        # Validate mode
        valid_modes = ['cool', 'heat', 'off']
        if mode not in valid_modes:
            messages.error(request, "Invalid mode selected.")
            return render(request, 'thermostat.html', {'thermostat': thermostat})

        try:
            # Update the thermostat's mode and save it
            thermostat.mode = mode
            thermostat.save()
            messages.success(request, "Thermostat updated successfully.")
        except Exception as e:
            # Handle unexpected errors (e.g., database issues)
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'thermostat.html', {'thermostat': thermostat})

        # Redirect after successful POST to avoid form re-submission on refresh
        return redirect('thermostat_detail', id=thermostat.id)

    # Render the template with the thermostat data if GET request
    return render(request, 'thermostat.html', {'thermostat': thermostat})


def thermostat_detail(request, id):
    thermostat = get_object_or_404(SmartThermostat, id=id)
    return render(request, 'thermostat_detail.html', {'thermostat': thermostat})

