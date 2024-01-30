"""
URL configuration for api_rotas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webhook_ba.views import webhook_ba
from webhook_mg.views import webhook_mg
from buonny_mg.views import buonny_mg

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhook_ba/', webhook_ba),
    path('webhook_mg/', webhook_mg),
    path('buonny_mg/', buonny_mg),
]
