
# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Home, Room, SmartDevice, CarCharger, SmartThermostat
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['home'] = Home.objects.filter(owner=user)
        context['rooms'] = Room.objects.filter(home__owner=user)
        context['devices'] = SmartDevice.objects.filter(owner=user)
        context['chargers'] = CarCharger.objects.filter(owner=user)
        return context



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
        return redirect('thermostat_view', id=thermostat.id)

    # Render the template with the thermostat data if GET request
    return render(request, 'thermostat.html', {'thermostat': thermostat})


def thermostat_detail(request, id):
    thermostat = get_object_or_404(SmartThermostat, id=id)
    return render(request, 'thermostat_detail.html', {'thermostat': thermostat})

