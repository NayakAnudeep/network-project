"""
URL configuration for aniTA project.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include("aniTA_app.urls")),
    path('users/', include("users.urls")),
    path('network/', include("network_simulation.urls")),
    path('admin/', admin.site.urls),
]