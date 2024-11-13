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
    path('thermostat/<int:id>/', views.thermostat_detail, name='thermostat_detail'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout')
]