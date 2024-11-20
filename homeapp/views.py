
from .forms import SmartThermostatForm, SmartBulbForm, CarChargerForm
from .models import Home, Room, SmartDevice, CarCharger, SmartThermostat, SmartBulb
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from .services import fetch_weather_data


@login_required(login_url='/accounts/login/')
def home_view(request):
    user = request.user

    home = Home.objects.filter(owner=user).first()
    if home is None:
        lon = 59.21
        lat = 10.92
        air_temperature, humidity, wind = fetch_weather_data(lat, lon)
    else:
        lon = home.lon
        lat = home.lat
        air_temperature, humidity, wind = fetch_weather_data(lat, lon)


    context = {
        'user': user,
        'home': home,
        'rooms': Room.objects.filter(home__owner=user),
        'thermostats': SmartThermostat.objects.filter(owner=user),
        'smartbulbs': SmartBulb.objects.filter(owner=user),
        'chargers': CarCharger.objects.filter(owner=user),
        'devices': SmartDevice.objects.filter(owner=user),
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
            smart_thermostat.owner = request.user
            smart_thermostat.save()
            return redirect(reverse_lazy('home'))
    else:
        form = SmartThermostatForm()

    return render(request, 'new_device.html', {'form': form})

def update_thermostat(request, id):
    thermostat = get_object_or_404(SmartThermostat, id=id)

    if request.method == "POST":
        mode = request.POST.get('mode')

        valid_modes = ['cool', 'heat', 'off']
        if mode not in valid_modes:
            messages.error(request, "Invalid mode selected.")
            return render(request, 'thermostat.html', {'thermostat': thermostat})

        try:
            thermostat.mode = mode
            thermostat.save()
            messages.success(request, "Thermostat updated successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, 'thermostat.html', {'thermostat': thermostat})
        return redirect('thermostat_detail', id=thermostat.id)
    return render(request, 'thermostat.html', {'thermostat': thermostat})

@login_required
def update_device_view(request, device_type, id):
    if device_type == 'smartbulb':
        model = SmartBulb
        form_class = SmartBulbForm
    elif device_type == 'carcharger':
        model = CarCharger
        form_class = CarChargerForm
    elif device_type == 'smartthermostat':
        model = SmartThermostat
        form_class = SmartThermostatForm
    else:
        return redirect(reverse_lazy('home'))
    device = get_object_or_404(model, id=id)

    if request.method == 'POST':
        form = form_class(request.POST, instance=device)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('home'))
    else:
        form = form_class(instance=device)
    return render(request, 'update_device.html', {'form': form, 'device_type': device_type})

'''
Disse er ikke i bruk.

@login_required
def delete_smart_thermostat_device_view(request, id):
    smart_thermostat = get_object_or_404(SmartThermostat, id=id)
    if request.method == 'POST':
        smart_thermostat.delete()
        return redirect(reverse_lazy('home'))
    return render(request, 'create_device.html', {'smart_thermostat': smart_thermostat})

#Brukes ikke
def thermostat_detail(request, id):
    thermostat = get_object_or_404(SmartThermostat, id=id)
    return render(request, 'thermostat_detail.html', {'thermostat': thermostat})

'''
@login_required
def update_device_temperature(request, device_type, id):
    if request.method == "POST":
        device = get_object_or_404(SmartThermostat, id=id)
        new_temperature = int(request.POST.get('temperature'))

        try:
            response_message = device.update_temperature(new_temperature)
            messages.success(request, response_message)
        except Exception as e:
            messages.error(request, f"Feil ved oppdatering av temperatur: {e}")
        return redirect('device_detail', device_type=device_type, id=id)

    messages.error(request, "Invalid request method.")
    return redirect(reverse('device_detail', kwargs={'device_type': device_type, 'id': id}))


@login_required
def new_device_list(request):
    return render(request, 'new_device_list.html')

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def device_detail_view(request, device_type, id):
    model_map = {
        'smartbulb': SmartBulb,
        'carcharger': CarCharger,
        'smartthermostat': SmartThermostat,
    }
    model = model_map.get(device_type.lower())

    if not model:
        return redirect('home')

    device = get_object_or_404(model, id=id)
    return render(request, 'device_detail.html', {'device': device, 'device_type': device_type})


@login_required
def new_device(request, device_type):
    if device_type == "smartbulb":
        form_class = SmartBulbForm
        model_name = "SmartBulb"
    elif device_type == "smartthermostat":
        form_class = SmartThermostatForm
        model_name = "SmartThermostat"
    elif device_type == "carcharger":
        form_class = CarChargerForm
        model_name = "CarCharger"
    else:
        return redirect(reverse_lazy('home'))

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.device_type = device_type
            device.owner = request.user
            device.save()
            return redirect(reverse_lazy('home'))
    else:
        form = form_class()
    return render(request, 'create_device.html', {'form': form, 'device_type': model_name})

@login_required
def delete_device_view(request, device_type, id):
    model_map = {
        'smartbulb': SmartBulb,
        'carcharger': CarCharger,
        'smartthermostat': SmartThermostat,
    }
    model = model_map.get(device_type.lower())

    if not model:
        return redirect(reverse_lazy('home'))

    device = get_object_or_404(model, id=id)

    if request.method == 'POST':
        device.delete()
        return redirect(reverse_lazy('home'))
    return render(request, 'delete_device.html', {'device': device, 'device_type': device_type})

@login_required
def toggle_light(request, device_type, id):

    if device_type != "smartbulb":
        return redirect('device_detail', device_type=device_type, id=id)

    bulb = get_object_or_404(SmartBulb, id=id)

    try:
        if bulb.is_on:
            response_message = bulb.turn_off()
            messages.success(request, response_message)
        else:
            response_message = bulb.turn_on()
            messages.success(request, response_message)
    except Exception as e:
        messages.error(request, f"Failed to toggle light: {e}")

    return redirect('device_detail', device_type=device_type, id=id)