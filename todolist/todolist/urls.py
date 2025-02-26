"""todolist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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


from autodoapp.views import ulogin, usignup, rpassword, ulogout
from django.contrib import admin
from django.urls import path
from todoapp.views import home, create, viewtask, deletetask
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ulogin, name='ulogin'),
    path('usignup/', usignup, name='usignup'),
    path('rpassword/', rpassword, name='rpassword'),
    path('ulogout/', ulogout, name="ulogout"),
    path("home/", home, name='home'),
    path('create/', create, name="create"),
    path("viewtask/", viewtask, name="viewtask"),
    path("deletetask/<str:t>/<str:da>", deletetask, name="deletetask")

]
