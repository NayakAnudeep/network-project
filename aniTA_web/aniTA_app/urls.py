from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="student_dashboard"),
    path("courses/", views.courses, name="all_courses"),
    # path("<int:arg_foo>/dashboard/", views.dashboard, name="dashboard"),
    path("users/", include('users.urls')),
]
