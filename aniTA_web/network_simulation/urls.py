from django.urls import path
from . import views
from . import views_visualization

app_name = 'network_simulation'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.network_dashboard, name='dashboard'),
    path('course-network/', views.course_network, name='course_network'),
    path('student-performance/', views.student_performance, name='student_performance'),
    
    # Knowledge graph role-specific dashboards
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    
    # Detail pages
    path('dashboard/student/<str:student_id>/', views.student_detail, name='student_detail'),
    path('dashboard/instructor/<str:instructor_id>/', views.instructor_detail, name='instructor_detail'),
    path('dashboard/course/<str:course_id>/', views.course_detail, name='course_detail'),
    
    # API routes for AJAX requests
    path('api/course-network/', views_visualization.api_course_network, name='api_course_network'),
    path('api/student-instructor-network/', views_visualization.api_student_instructor_network, name='api_student_instructor_network'),
    path('api/student-performance/', views_visualization.api_student_performance, name='api_student_performance'),
    path('api/section/<str:section_id>/', views_visualization.api_section_detail, name='api_section_detail'),
    
    # Source material and section views
    path('source-materials/', views.source_materials_list, name='source_materials_list'),
    path('source-material/<str:material_id>/', views.source_material_detail, name='source_material_detail'),
    path('section/<str:section_id>/', views.section_detail, name='section_detail'),
    path('student-recommendations/<str:student_id>/', views.student_section_recommendations, name='student_section_recommendations'),
    path('instructor-problem-sections/<str:instructor_id>/', views.instructor_problem_sections, name='instructor_problem_sections'),
]