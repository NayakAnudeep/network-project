from django.http import JsonResponse
import json
import logging
import random
import networkx as nx

def api_course_network(request):
    """API endpoint for course network visualization data"""
    try:
        # Create sample course network data for visualization
        network_data = {
            'nodes': [
                {'id': i, 'name': f'Course {i}', 'group': random.randint(1, 3)} 
                for i in range(1, 11)
            ],
            'links': []
        }
        
        # Create links between courses
        G = nx.erdos_renyi_graph(10, 0.3)
        for u, v in G.edges():
            network_data['links'].append({
                'source': u,
                'target': v,
                'weight': random.randint(1, 5)
            })
        
        return JsonResponse(network_data)
    except Exception as e:
        logging.error(f"Error in api_course_network: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_student_instructor_network(request):
    """API endpoint for student-instructor network visualization data"""
    try:
        # Create sample student-instructor network data for visualization
        nodes = []
        links = []
        
        # Create instructor nodes
        for i in range(1, 6):
            nodes.append({
                'id': f'I{i}',
                'name': f'Professor {i}',
                'group': 1
            })
        
        # Create student nodes
        for i in range(1, 21):
            nodes.append({
                'id': f'S{i}',
                'name': f'Student {i}',
                'group': 2
            })
        
        # Create links between students and instructors
        for s in range(1, 21):
            # Each student connects to 1-3 instructors
            instructors = random.sample(range(1, 6), random.randint(1, 3))
            for i in instructors:
                links.append({
                    'source': f'S{s}',
                    'target': f'I{i}',
                    'weight': random.randint(1, 5)
                })
        
        network_data = {
            'nodes': nodes,
            'links': links
        }
        
        return JsonResponse(network_data)
    except Exception as e:
        logging.error(f"Error in api_student_instructor_network: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_student_performance(request):
    """API endpoint for student performance visualization data"""
    try:
        # Create sample student performance data for visualization
        performance_data = {
            'grade_distribution': {
                'A': random.randint(10, 30),
                'B': random.randint(20, 40),
                'C': random.randint(15, 30),
                'D': random.randint(5, 15),
                'F': random.randint(1, 10)
            },
            'assessment_performance': {
                'labels': ['Quiz 1', 'Quiz 2', 'Midterm', 'Project', 'Final'],
                'datasets': [
                    {
                        'label': 'Class Average',
                        'data': [
                            random.randint(65, 85) for _ in range(5)
                        ],
                        'backgroundColor': 'rgba(54, 162, 235, 0.5)'
                    },
                    {
                        'label': 'Top Students',
                        'data': [
                            random.randint(85, 95) for _ in range(5)
                        ],
                        'backgroundColor': 'rgba(75, 192, 192, 0.5)'
                    }
                ]
            },
            'student_progress': {
                'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
                'datasets': [
                    {
                        'label': 'Average Score',
                        'data': [
                            random.randint(70, 90) for _ in range(6)
                        ],
                        'borderColor': 'rgba(75, 192, 192, 1)',
                        'fill': False
                    }
                ]
            }
        }
        
        return JsonResponse(performance_data)
    except Exception as e:
        logging.error(f"Error in api_student_performance: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_section_detail(request, section_id):
    """API endpoint for section detail data"""
    try:
        # Create sample section data
        section_data = {
            'id': section_id,
            'title': f'Section {section_id}',
            'content': f'This is the content for section {section_id}. It includes important concepts and examples.',
            'importance_score': random.randint(70, 95),
            'related_sections': [
                {'id': section_id + 1, 'title': f'Section {section_id + 1}', 'similarity': random.randint(60, 90)},
                {'id': section_id + 2, 'title': f'Section {section_id + 2}', 'similarity': random.randint(40, 80)}
            ]
        }
        
        return JsonResponse(section_data)
    except Exception as e:
        logging.error(f"Error in api_section_detail: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_mistake_clusters(request):
    """API endpoint for mistake clusters visualization data"""
    try:
        # Create sample mistake clusters data
        clusters_data = {
            'clusters': [
                {
                    'id': 1,
                    'name': 'Conceptual Misunderstandings',
                    'count': random.randint(10, 30),
                    'students': random.randint(5, 15)
                },
                {
                    'id': 2,
                    'name': 'Calculation Errors',
                    'count': random.randint(20, 40),
                    'students': random.randint(10, 20)
                },
                {
                    'id': 3,
                    'name': 'Application Mistakes',
                    'count': random.randint(15, 35),
                    'students': random.randint(8, 18)
                },
                {
                    'id': 4,
                    'name': 'Problem-Solving Approach',
                    'count': random.randint(10, 25),
                    'students': random.randint(5, 15)
                }
            ],
            'connections': [
                {'source': 1, 'target': 2, 'strength': random.random() * 0.5 + 0.3},
                {'source': 1, 'target': 3, 'strength': random.random() * 0.4 + 0.2},
                {'source': 2, 'target': 4, 'strength': random.random() * 0.3 + 0.1},
                {'source': 3, 'target': 4, 'strength': random.random() * 0.6 + 0.2}
            ]
        }
        
        return JsonResponse(clusters_data)
    except Exception as e:
        logging.error(f"Error in api_mistake_clusters: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_student_mistakes(request, student_id):
    """API endpoint for student mistakes data"""
    try:
        # Create sample student mistakes data
        mistakes_data = {
            'student_id': student_id,
            'mistakes': [
                {
                    'id': 1,
                    'description': 'Incorrect application of formula',
                    'frequency': random.randint(2, 5),
                    'section_id': random.randint(1, 10),
                    'section_title': f'Section {random.randint(1, 10)}'
                },
                {
                    'id': 2,
                    'description': 'Conceptual misunderstanding',
                    'frequency': random.randint(1, 4),
                    'section_id': random.randint(1, 10),
                    'section_title': f'Section {random.randint(1, 10)}'
                },
                {
                    'id': 3,
                    'description': 'Calculation error',
                    'frequency': random.randint(3, 7),
                    'section_id': random.randint(1, 10),
                    'section_title': f'Section {random.randint(1, 10)}'
                }
            ],
            'recommendations': [
                {
                    'id': 1,
                    'title': 'Review core concepts',
                    'section_id': random.randint(1, 10),
                    'importance': random.randint(70, 95)
                },
                {
                    'id': 2,
                    'title': 'Practice problem-solving techniques',
                    'section_id': random.randint(1, 10),
                    'importance': random.randint(60, 90)
                }
            ]
        }
        
        return JsonResponse(mistakes_data)
    except Exception as e:
        logging.error(f"Error in api_student_mistakes: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_instructor_mistake_heatmap(request, instructor_id):
    """API endpoint for instructor mistake heatmap data"""
    try:
        # Create sample mistake heatmap data
        sections = [f'Section {i}' for i in range(1, 11)]
        mistake_types = ['Conceptual', 'Calculation', 'Application', 'Problem-Solving']
        
        heatmap_data = {
            'instructor_id': instructor_id,
            'sections': sections,
            'mistake_types': mistake_types,
            'heatmap': []
        }
        
        # Generate heatmap data
        for section in sections:
            for mistake in mistake_types:
                heatmap_data['heatmap'].append({
                    'section': section,
                    'mistake': mistake,
                    'value': random.randint(1, 20)
                })
        
        return JsonResponse(heatmap_data)
    except Exception as e:
        logging.error(f"Error in api_instructor_mistake_heatmap: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)