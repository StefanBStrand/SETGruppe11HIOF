"""
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import home_view
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create_smart_thermostat_device/', views.create_smart_thermostat_device_view, name='create_smart_thermostat_device'),
    path('update_thermostat/<int:id>/', views.update_thermostat, name='update_thermostat'),
    path('new_device_list/', views.new_device_list, name='new_device_list'),
    path('new_device/<str:device_type>/', views.new_device, name='new_device'),
    path('settings/', views.settings, name='settings'),
    path('delete_device/<str:device_type>/<int:id>/', views.delete_device_view, name='delete_device'),
    path('device/<str:device_type>/<int:id>/', views.device_detail_view, name='device_detail'),
    path('update_device/<str:device_type>/<int:id>/', views.update_device_view, name='update_device'),
    path('thermostat/<int:id>/', views.thermostat_detail, name='thermostat_detail'),
    path('device/<str:device_type>/<int:id>/update-temperature/', views.update_device_temperature, name='update_device_temperature'),
    #path('device/<int:id>/', views.device_detail_view, name='device_detail'),
    path('device/<str:device_type>/<int:id>/toggle-light/', views.toggle_light, name='toggle_light'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout')
]