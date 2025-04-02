from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="student_dashboard"),
    path("instructor-dashboard/", views.instructor_dashboard, name="instructor_dashboard"),
    path("courses/", views.courses, name="all_courses"),
    path("course/<int:course_id>/", views.course, name='course'),
    path("users/", include('users.urls')),
    path("add_class/", views.add_class, name='add_class'),
    path("student_add_course_post/", views.student_add_course_post, name='student_add_course_post'),
    path("student-add-class/", views.student_add_course_get, name='student_add_course_get'),
    path("add_assignment/", views.add_assignment, name="add_assignment")
]
