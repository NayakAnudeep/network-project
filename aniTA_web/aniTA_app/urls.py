from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("users/", include('users.urls'))
    # path("login/", views.login, name="login"),
    # path("signup/", views.signup, name="signup")
    # path("<int:arg_foo>/dashboard/", views.dashboard, name="dashboard")
]
