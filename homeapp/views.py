from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Home, Room, SmartDevice, CarCharger, SmartThermostat
from django.http import JsonResponse


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


# View using render() for Django templates
def update_thermostat(request, id):
    if request.method == 'POST':
        thermostat = SmartThermostat.objects.get(id=id)
        mode = request.POST.get('mode')
        thermostat.mode = mode
        thermostat.save()
        context = {
            'status': 'updated',
            'new_temperature': thermostat.set_temperature,
            'new_mode': thermostat.mode
        }
        return render(request, 'thermostat.html', context)
