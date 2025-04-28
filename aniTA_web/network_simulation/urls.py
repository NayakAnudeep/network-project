from django.urls import path
from . import views

app_name = 'network_simulation'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.network_dashboard, name='dashboard'),
    path('student-instructor-network/', views.student_instructor_network, name='student_instructor_network'),
    path('course-network/', views.course_network, name='course_network'),
    path('student-performance/', views.student_performance, name='student_performance'),
    
    # Knowledge graph role-specific dashboards
    path('student-dashboard/', views.student_analytics_dashboard, name='student_dashboard'),
    path('instructor-dashboard/', views.instructor_analytics_dashboard, name='instructor_dashboard'),
    
    # Detail pages
    path('dashboard/student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('dashboard/instructor/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),
    path('dashboard/course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # API routes for AJAX requests
    path('api/course-network/', views.api_course_network, name='api_course_network'),
    path('api/student-instructor-network/', views.api_student_instructor_network, name='api_student_instructor_network'),
    path('api/student-performance/', views.api_student_performance, name='api_student_performance'),
    
    # Knowledge graph API endpoints
    path('api/section/<int:section_id>/', views.api_section_detail, name='api_section_detail'),
    path('api/mistake-clusters/', views.api_mistake_clusters, name='api_mistake_clusters'),
    path('api/student-mistakes/<int:student_id>/', views.api_student_mistakes, name='api_student_mistakes'),
    path('api/instructor-mistake-heatmap/<int:instructor_id>/', views.api_instructor_mistake_heatmap, name='api_instructor_mistake_heatmap'),
    
    # New ArangoDB analysis endpoints
    path('api/arango/student-weaknesses/<str:student_id>/', views.api_arango_student_weaknesses, name='api_arango_student_weaknesses'),
    path('api/arango/instructor-insights/<str:instructor_id>/', views.api_arango_instructor_insights, name='api_arango_instructor_insights'),
    path('api/arango/grading-inconsistencies/', views.api_arango_grading_inconsistencies, name='api_arango_grading_inconsistencies'),
    path('api/arango/course-material-recommendations/<str:student_id>/', views.api_arango_course_recommendations, name='api_arango_course_recommendations'),
    
    # Source material and section views
    path('source-materials/', views.source_materials_list, name='source_materials_list'),
    path('source-material/<str:material_id>/', views.source_material_detail, name='source_material_detail'),
    path('section/<str:section_id>/', views.section_detail, name='section_detail'),
    path('student-recommendations/<str:student_id>/', views.student_section_recommendations, name='student_section_recommendations'),
    path('instructor-problem-sections/<str:instructor_id>/', views.instructor_problem_sections, name='instructor_problem_sections'),
]