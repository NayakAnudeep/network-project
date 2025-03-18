from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="student_dashboard"),
    path("courses/", views.courses, name="all_courses"),
    path("users/", include('users.urls')),
]
