from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="student_dashboard"),
    path("instructor-dashboard/", views.instructor_dashboard, name="instructor_dashboard"),
    path("instructor/add-class", views.instructor_add_class, name="instructor_add_class"),
    path("instructor/course/<str:course_code>", views.instructor_course, name="instructor_course"),
    path("instructor/course/<str:course_code>/add-assignment", views.instructor_course_add_assignment, name="instructor_course_add_assignment"),
    path("submissions/<str:course_code>/<str:assignment_id>", views.class_assignment_submissions, name="class_assignment_submissions"),
    path("courses/", views.courses, name="all_courses"),
    path("course/<int:course_id>/", views.course, name='course'),
    path("users/", include('users.urls')),
    path("add_class/", views.add_class, name='add_class'),
    path("student_add_course_post/", views.student_add_course_post, name='student_add_course_post'),
    path("student-add-class/", views.student_add_course_get, name='student_add_course_get'),
    path("add_assignment/", views.add_assignment, name="add_assignment"),
    path("upload_assignment/<str:class_code>/<str:assignment_id>", views.upload, name='upload_assignment'),
    path("view_pdf/<str:submission_id>", views.view_pdf, name='view_pdf')
]
