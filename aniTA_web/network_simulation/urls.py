from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='network_index'),
    path('dashboard/', views.network_dashboard, name='network_dashboard'),
    path('student-network/', views.student_network, name='student_network'),
    path('course-network/', views.course_network, name='course_network'),
]