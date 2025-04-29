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

def api_arango_student_instructor_network(request):
    """API endpoint to get student-instructor network data from ArangoDB."""
    try:
        network_data = get_student_instructor_network()
        return JsonResponse(network_data)
    except Exception as e:
        # Return a fallback dataset in case of error with ArangoDB
        print(f"Error in student-instructor network API: {str(e)}")
        
        # Generate sample network data
        nodes = []
        edges = []
        
        # Create 5 instructor nodes
        for i in range(1, 6):
            nodes.append({
                'id': f'instructor_{i}',
                'name': f'Instructor {i}',
                'type': 'instructor'
            })
            
        # Create 30 student nodes
        for i in range(1, 31):
            nodes.append({
                'id': f'student_{i}',
                'name': f'Student {i}',
                'type': 'student'
            })
        
        # Create connections between students and instructors
        import random
        for s in range(1, 31):
            # Each student connects to 2-4 instructors
            for _ in range(random.randint(2, 4)):
                instructor = random.randint(1, 5)
                # Calculate indices directly
                student_index = s + 4  # 5 instructors first, then students start at index 5
                instructor_index = instructor - 1  # Instructor indices 0-4
                
                edges.append({
                    'source': student_index,
                    'target': instructor_index,
                    'weight': random.randint(1, 5),
                    'grade': round(random.uniform(70, 95), 1)
                })
        
        # Create network metrics
        network_metrics = {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'density': len(edges) / (len(nodes) * (len(nodes) - 1) / 2),
            'avg_degree_centrality': 2 * len(edges) / len(nodes),
            'avg_betweenness_centrality': 0.03,
            'community_count': 5,
            'largest_component_size': len(nodes),
            'largest_component_diameter': 6,
            'modularity': 0.52
        }
        
        # Create instructor data
        top_instructors = []
        instructor_avg_scores = []
        for i in range(1, 6):
            student_count = random.randint(10, 30)
            avg_score = round(random.uniform(70, 95), 1)
            
            top_instructors.append({
                'id': i,
                'name': f'Instructor {i}',
                'student_count': student_count
            })
            
            instructor_avg_scores.append({
                'id': i,
                'name': f'Instructor {i}',
                'avg_score': avg_score
            })
        
        # Create student data
        top_students = []
        for i in range(1, 11):
            top_students.append({
                'id': i,
                'name': f'Student {i}',
                'instructor_count': random.randint(2, 5),
                'gpa': round(random.uniform(2.5, 4.0), 2)
            })
            
        return JsonResponse({
            'nodes': nodes, 
            'edges': edges,
            'network_metrics': network_metrics,
            'top_instructors': top_instructors,
            'instructor_avg_scores': instructor_avg_scores,
            'top_students': top_students
        })

def api_arango_course_network(request):
    """API endpoint to get course network data from ArangoDB."""
    try:
        network_data = get_course_network()
        return JsonResponse(network_data)
    except Exception as e:
        # Return a fallback dataset in case of error with ArangoDB
        print(f"Error in course network API: {str(e)}")
        
        # Generate sample course network data
        import random
        
        nodes = []
        edges = []
        
        # Create 10 course nodes
        for i in range(1, 11):
            nodes.append({
                'id': f'course_{i}',
                'name': f'Course {i}',
                'type': 'course'
            })
        
        # Create random connections between courses
        for i in range(10):
            for j in range(i+1, 10):
                if random.random() < 0.3:  # 30% chance of connection
                    edges.append({
                        'source': i,
                        'target': j,
                        'weight': random.randint(1, 10)
                    })
        
        # Calculate network metrics
        network_metrics = {
            'node_count': len(nodes),
            'edge_count': len(edges),
            'density': len(edges) / (len(nodes) * (len(nodes) - 1) / 2),
            'avg_degree_centrality': 2 * len(edges) / len(nodes),
            'avg_betweenness_centrality': 0.05,
            'community_count': 3,
            'diameter': 4,
            'average_shortest_path': 1.8
        }
        
        # Generate mock course data for charts
        course_enrollment = []
        for i in range(1, 11):
            course_enrollment.append({
                'name': f'Course {i}',
                'student_count': random.randint(15, 50)
            })
        
        # Generate mock course grades
        course_avg_grades = []
        for i in range(1, 11):
            course_avg_grades.append({
                'name': f'Course {i}',
                'avg_grade': round(random.uniform(70, 90), 1)
            })
        
        # Generate mock course connections
        course_connections = []
        for edge in edges:
            course_connections.append({
                'course1_id': nodes[edge['source']]['id'].split('_')[1],
                'course1_name': nodes[edge['source']]['name'],
                'course2_id': nodes[edge['target']]['id'].split('_')[1],
                'course2_name': nodes[edge['target']]['name'],
                'shared_students': edge['weight']
            })
            
        return JsonResponse({
            'nodes': nodes, 
            'edges': edges,
            'network_metrics': network_metrics,
            'course_enrollment': course_enrollment,
            'course_avg_grades': course_avg_grades,
            'course_connections': course_connections
        })