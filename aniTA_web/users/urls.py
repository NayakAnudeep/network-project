from django.urls import path 
from .views import register, login

urlpatterns = [
    path('register/', register, name = "register_api"), 
    path('login/', login, name = "login_api"),
]
