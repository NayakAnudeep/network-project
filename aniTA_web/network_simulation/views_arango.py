"""
ArangoDB-based views for network simulation.

This module provides view functions that use ArangoDB for educational analytics.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

from .arango_network_analysis import (
    get_student_instructor_network,
    get_course_network,
    detect_grading_inconsistencies,
    get_student_weaknesses,
    get_instructor_teaching_insights,
    get_course_material_recommendations
)

# API view functions for ArangoDB-based analytics

@login_required
def api_arango_student_weaknesses(request, student_id):
    """API endpoint to get a student's weak areas using ArangoDB."""
    try:
        results = get_student_weaknesses(student_id)
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_arango_instructor_insights(request, instructor_id):
    """API endpoint to get teaching insights for an instructor using ArangoDB."""
    try:
        results = get_instructor_teaching_insights(instructor_id)
        return JsonResponse(results)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_arango_grading_inconsistencies(request):
    """API endpoint to detect grading inconsistencies using ArangoDB."""
    try:
        # Optional instructor ID filter
        instructor_id = request.GET.get('instructor_id')
        results = detect_grading_inconsistencies(instructor_id)
        return JsonResponse({'inconsistencies': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_arango_course_recommendations(request, student_id):
    """API endpoint to get personalized course material recommendations for a student."""
    try:
        results = get_course_material_recommendations(student_id)
        return JsonResponse({'recommendations': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Enhanced network visualization endpoints using ArangoDB

@login_required
def api_arango_student_instructor_network(request):
    """API endpoint to get student-instructor network data from ArangoDB."""
    try:
        network_data = get_student_instructor_network()
        return JsonResponse(network_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_arango_course_network(request):
    """API endpoint to get course network data from ArangoDB."""
    try:
        network_data = get_course_network()
        return JsonResponse(network_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)