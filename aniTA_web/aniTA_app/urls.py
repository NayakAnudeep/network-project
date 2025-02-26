from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:arg_foo>/dashboard/", views.dashboard, name="dashboard")
]
