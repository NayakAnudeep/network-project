"""
URL Configuration for aniTA_web project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('network/', include('network_simulation.urls')),  # Network analysis dashboard
]
