from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Home, Room, SmartDevice, CarCharger

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
        context['chargers'] = CarCharger.objects.filter(home__owner=user)
        return context
