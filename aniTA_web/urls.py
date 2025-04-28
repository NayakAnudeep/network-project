"""
URL Configuration for aniTA_web project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Redirect to aniTA_server URLs which are the actual application URLs
    path('', include('aniTA_server.urls')),
]
