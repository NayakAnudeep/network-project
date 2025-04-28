from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.db import models
from django.contrib.auth.decorators import login_required
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import json
import random
import logging
from users.arangodb import db
from .graph_analysis import (
    get_student_mistakes,
    get_student_weakest_areas,
    get_section_recommendations,
    get_instructor_mistake_heatmap,
    get_top_common_mistakes,
    detect_grading_inconsistencies,
    get_mistake_clusters_with_stats
)

# Import ArangoDB network analysis functions
from .arango_network_analysis import (
    get_student_instructor_network,
    get_course_network,
    detect_grading_inconsistencies as arango_detect_grading_inconsistencies,
    get_student_weaknesses,
    get_instructor_teaching_insights,
    get_course_material_recommendations
)

# Import ArangoDB-specific views
from .views_arango import (
    api_arango_student_weaknesses,
    api_arango_instructor_insights,
    api_arango_grading_inconsistencies,
    api_arango_course_recommendations,
    api_arango_student_instructor_network,
    api_arango_course_network
)

# Import source material views
from .views_source_material import (
    source_materials_list,
    source_material_detail,
    section_detail,
    student_section_recommendations,
    instructor_problem_sections
)

# Safe import of models - if database not set up yet
try:
    from .models import Student, Instructor, Course, Assessment
    MODELS_AVAILABLE = True
except Exception as e:
    # This happens during migrations or if database tables are not created yet
    MODELS_AVAILABLE = False
    Student = Instructor = Course = Assessment = None
    logging.warning(f"Could not import network simulation models: {str(e)}")

def index(request):
    """Network simulation landing page"""
    return render(request, 'network_simulation/index.html', {
        'title': 'Network Analysis Dashboard'
    })

def network_dashboard(request):
    """Main dashboard for network analytics"""
    try:
        # Create a sample network graph
        G = nx.erdos_renyi_graph(50, 0.1)
        
        # Convert graph to visualization
        plt.figure(figsize=(10, 8))
        nx.draw(G, with_labels=False, node_color='lightblue', 
                node_size=50, alpha=0.8, edgecolors='gray')
        
        # Save plot to a base64 encoded image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
    
        # Get counts for sidebar statistics
        if MODELS_AVAILABLE:
            student_count = Student.objects.count()
            instructor_count = Instructor.objects.count()
            course_count = Course.objects.count()
            assessment_count = Assessment.objects.count()
        else:
            # Provide dummy data if models are not available
            student_count = random.randint(50, 200)
            instructor_count = random.randint(10, 30)
            course_count = random.randint(20, 50)
            assessment_count = random.randint(200, 500)
    
        return render(request, 'network_simulation/dashboard.html', {
            'title': 'Network Dashboard',
            'graph_image': graph_image,
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'student_count': student_count,
            'instructor_count': instructor_count,
            'course_count': course_count,
            'assessment_count': assessment_count
        })
    except Exception as e:
        logging.error(f"Error in network_dashboard view: {str(e)}")
        # Return a simplified view without the graph if there's an error
        return render(request, 'network_simulation/dashboard.html', {
            'title': 'Network Dashboard',
            'error_message': 'Error generating network graph.',
            'node_count': 0,
            'edge_count': 0,
            'student_count': 0,
            'instructor_count': 0,
            'course_count': 0,
            'assessment_count': 0
        })

def student_instructor_network(request):
    """Visualize student-instructor relationships network"""
    # Get counts for sidebar statistics
    if MODELS_AVAILABLE:
        student_count = Student.objects.count()
        instructor_count = Instructor.objects.count()
        course_count = Course.objects.count()
        assessment_count = Assessment.objects.count()
    else:
        # Provide dummy data if models are not available
        student_count = random.randint(50, 200)
        instructor_count = random.randint(10, 30)
        course_count = random.randint(20, 50)
        assessment_count = random.randint(200, 500)
    
    return render(request, 'network_simulation/student_instructor_network.html', {
        'title': 'Student-Instructor Network',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def course_network(request):
    """Visualize course relationships network"""
    # Get counts for sidebar statistics
    if MODELS_AVAILABLE:
        student_count = Student.objects.count()
        instructor_count = Instructor.objects.count()
        course_count = Course.objects.count()
        assessment_count = Assessment.objects.count()
    else:
        # Provide dummy data if models are not available
        student_count = random.randint(50, 200)
        instructor_count = random.randint(10, 30)
        course_count = random.randint(20, 50)
        assessment_count = random.randint(200, 500)
    
    return render(request, 'network_simulation/course_network.html', {
        'title': 'Course Relationship Network',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def student_performance(request):
    """Visualize student performance metrics"""
    # Get counts for sidebar statistics
    if MODELS_AVAILABLE:
        student_count = Student.objects.count()
        instructor_count = Instructor.objects.count()
        course_count = Course.objects.count()
        assessment_count = Assessment.objects.count()
    else:
        # Provide dummy data if models are not available
        student_count = random.randint(50, 200)
        instructor_count = random.randint(10, 30)
        course_count = random.randint(20, 50)
        assessment_count = random.randint(200, 500)
    
    return render(request, 'network_simulation/student_performance.html', {
        'title': 'Student Performance Analytics',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def student_detail(request, student_id):
    """Detail view for a specific student"""
    try:
        if MODELS_AVAILABLE:
            # Attempt to fetch from database
            try:
                student_obj = get_object_or_404(Student, pk=student_id)
                student = {
                    'id': student_id,
                    'name': student_obj.name,
                    'email': f'{student_obj.student_id.lower()}@example.com',
                    'year': student_obj.year,
                    'major': student_obj.major,
                    'gpa': student_obj.gpa,
                    'courses': Enrollment.objects.filter(student=student_obj).count(),
                    'avg_grade': Assessment.objects.filter(student=student_obj).aggregate(avg=models.Avg('score'))['avg'] or 0
                }
                
                # Get enrollments
                enrollments = Enrollment.objects.filter(student=student_obj)
                courses = [{
                    'id': enroll.course.course_id,
                    'name': enroll.course.name,
                    'term': enroll.term,
                    'year': enroll.year,
                    'final_grade': enroll.final_grade or 0
                } for enroll in enrollments]
                
                # Get assessments
                assessments = Assessment.objects.filter(student=student_obj).order_by('-date')[:10]
                assessment_list = [{
                    'course': assessment.course.name,
                    'type': assessment.type,
                    'date': assessment.date,
                    'score': assessment.score
                } for assessment in assessments]
                
                # Get instructor average scores
                instructor_avg_scores = []
                for instructor in Instructor.objects.filter(assessments__student=student_obj).distinct():
                    avg_score = Assessment.objects.filter(
                        student=student_obj, 
                        instructor=instructor
                    ).aggregate(avg=models.Avg('score'))['avg'] or 0
                    instructor_avg_scores.append({
                        'id': instructor.instructor_id,
                        'name': instructor.name,
                        'avg_score': round(avg_score, 1)
                    })
                
            except Exception as e:
                # Fall back to dummy data if error occurs
                logging.warning(f"Error fetching student data: {str(e)}")
                raise Http404("Student not found")
        else:
            # Use dummy data if models are not available
            student = {
                'id': student_id,
                'name': f'Student {student_id}',
                'email': f'student{student_id}@example.com',
                'year': random.randint(1, 4),
                'major': random.choice(['Computer Science', 'Engineering', 'Mathematics', 'Physics']),
                'gpa': round(random.uniform(2.5, 4.0), 2),
                'courses': random.randint(3, 6),
                'avg_grade': round(random.uniform(70, 95), 2)
            }
            
            # Dummy courses
            courses = []
            for i in range(1, student['courses'] + 1):
                courses.append({
                    'id': f'CS{100+i}',
                    'name': f'Course {i}',
                    'term': random.choice([1, 2]),
                    'year': 2023,
                    'final_grade': round(random.uniform(60, 100), 1)
                })
            
            # Dummy assessments
            assessment_list = []
            for i in range(1, 8):
                assessment_list.append({
                    'course': f'Course {random.randint(1, student["courses"])}',
                    'type': random.choice(['Quiz', 'Exam', 'Project', 'Homework']),
                    'date': f'2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'score': round(random.uniform(60, 100), 1)
                })
            
            # Dummy instructor scores
            instructor_avg_scores = []
            for i in range(1, 4):
                instructor_avg_scores.append({
                    'id': i,
                    'name': f'Instructor {i}',
                    'avg_score': round(random.uniform(70, 95), 1)
                })
    
        # Get counts for sidebar statistics
        student_count = Student.objects.count() if MODELS_AVAILABLE else random.randint(50, 200)
        instructor_count = Instructor.objects.count() if MODELS_AVAILABLE else random.randint(10, 30)
        course_count = Course.objects.count() if MODELS_AVAILABLE else random.randint(20, 50)
        assessment_count = Assessment.objects.count() if MODELS_AVAILABLE else random.randint(200, 500)
        
        return render(request, 'network_simulation/student_detail.html', {
            'title': f'Student: {student["name"]}',
            'student': student,
            'courses': courses,
            'assessments': assessment_list,
            'instructor_avg_scores': instructor_avg_scores,
            'student_count': student_count,
            'instructor_count': instructor_count,
            'course_count': course_count,
            'assessment_count': assessment_count
        })
        
    except Exception as e:
        logging.error(f"Error in student_detail view: {str(e)}")
        raise Http404("Student not found")

def instructor_detail(request, instructor_id):
    """Detail view for a specific instructor"""
    try:
        if MODELS_AVAILABLE:
            # Attempt to fetch from database
            try:
                instructor_obj = get_object_or_404(Instructor, pk=instructor_id)
                instructor = {
                    'id': instructor_id,
                    'name': instructor_obj.name,
                    'email': f'{instructor_obj.instructor_id.lower()}@example.com',
                    'department': instructor_obj.department,
                    'specialization': instructor_obj.specialization,
                    'courses': instructor_obj.courses.count(),
                    'students': Enrollment.objects.filter(course__instructors=instructor_obj).values('student').distinct().count()
                }
                
                # Get courses
                courses = []
                for course in instructor_obj.courses.all():
                    student_count = Enrollment.objects.filter(course=course).count()
                    courses.append({
                        'id': course.course_id,
                        'name': course.name,
                        'credits': course.credits,
                        'student_count': student_count
                    })
                
                # Get students with assessments by this instructor
                students_data = []
                students = Student.objects.filter(assessments__instructor=instructor_obj).distinct()
                for student in students:
                    assessments = Assessment.objects.filter(student=student, instructor=instructor_obj)
                    avg_score = assessments.aggregate(avg=models.Avg('score'))['avg'] or 0
                    assessment_count = assessments.count()
                    students_data.append({
                        'id': student.student_id,
                        'name': student.name,
                        'year': student.year,
                        'gpa': student.gpa,
                        'assessment_count': assessment_count,
                        'avg_score': round(avg_score, 1)
                    })
                
                # Get assessment type averages
                type_avg_scores = []
                assessment_types = Assessment.objects.filter(instructor=instructor_obj).values_list('type', flat=True).distinct()
                for type_name in assessment_types:
                    count = Assessment.objects.filter(instructor=instructor_obj, type=type_name).count()
                    avg_score = Assessment.objects.filter(instructor=instructor_obj, type=type_name).aggregate(avg=models.Avg('score'))['avg'] or 0
                    type_avg_scores.append({
                        'type': type_name,
                        'count': count,
                        'avg_score': round(avg_score, 1)
                    })
                
                # Get course average scores
                course_avg_scores = []
                for course in instructor_obj.courses.all():
                    avg_score = Assessment.objects.filter(instructor=instructor_obj, course=course).aggregate(avg=models.Avg('score'))['avg'] or 0
                    course_avg_scores.append({
                        'id': course.course_id,
                        'name': course.name,
                        'avg_score': round(avg_score, 1)
                    })
                
            except Exception as e:
                # Fall back to dummy data if error occurs
                logging.warning(f"Error fetching instructor data: {str(e)}")
                raise Http404("Instructor not found")
        else:
            # Use dummy data if models are not available
            instructor = {
                'id': instructor_id,
                'name': f'Instructor {instructor_id}',
                'email': f'instructor{instructor_id}@example.com',
                'department': random.choice(['Computer Science', 'Engineering', 'Mathematics', 'Physics']),
                'specialization': random.choice(['Algorithms', 'Machine Learning', 'Databases', 'Networking']),
                'courses': random.randint(2, 5),
                'students': random.randint(30, 100)
            }
            
            # Dummy courses
            courses = []
            for i in range(1, instructor['courses'] + 1):
                courses.append({
                    'id': f'CS{100+i}',
                    'name': f'Course {i}',
                    'credits': random.randint(1, 4),
                    'student_count': random.randint(15, 40)
                })
            
            # Dummy students
            students_data = []
            for i in range(1, 11):
                students_data.append({
                    'id': i,
                    'name': f'Student {i}',
                    'year': random.randint(1, 4),
                    'gpa': round(random.uniform(2.5, 4.0), 2),
                    'assessment_count': random.randint(3, 10),
                    'avg_score': round(random.uniform(70, 95), 1)
                })
            
            # Dummy assessment types
            type_avg_scores = []
            for type_name in ['Quiz', 'Exam', 'Project', 'Homework']:
                type_avg_scores.append({
                    'type': type_name,
                    'count': random.randint(5, 20),
                    'avg_score': round(random.uniform(70, 90), 1)
                })
            
            # Dummy course scores
            course_avg_scores = []
            for i, course in enumerate(courses):
                course_avg_scores.append({
                    'id': course['id'],
                    'name': course['name'],
                    'avg_score': round(random.uniform(70, 90), 1)
                })
    
        # Get counts for sidebar statistics
        student_count = Student.objects.count() if MODELS_AVAILABLE else random.randint(50, 200)
        instructor_count = Instructor.objects.count() if MODELS_AVAILABLE else random.randint(10, 30)
        course_count = Course.objects.count() if MODELS_AVAILABLE else random.randint(20, 50)
        assessment_count = Assessment.objects.count() if MODELS_AVAILABLE else random.randint(200, 500)
        
        return render(request, 'network_simulation/instructor_detail.html', {
            'title': f'Instructor: {instructor["name"]}',
            'instructor': instructor,
            'courses': courses,
            'students': students_data,
            'type_avg_scores': type_avg_scores,
            'course_avg_scores': course_avg_scores,
            'student_count': student_count,
            'instructor_count': instructor_count,
            'course_count': course_count,
            'assessment_count': assessment_count
        })
        
    except Exception as e:
        logging.error(f"Error in instructor_detail view: {str(e)}")
        raise Http404("Instructor not found")

def course_detail(request, course_id):
    """Detail view for a specific course"""
    try:
        if MODELS_AVAILABLE:
            # Attempt to fetch from database
            try:
                course_obj = get_object_or_404(Course, pk=course_id)
                enrollment_count = Enrollment.objects.filter(course=course_obj).count()
                assessment_count_course = Assessment.objects.filter(course=course_obj).count()
                
                course = {
                    'id': course_id,
                    'name': course_obj.name,
                    'code': course_obj.course_id,
                    'credits': course_obj.credits,
                    'students': enrollment_count
                }
                
                # Get instructors
                instructors = []
                for instructor in course_obj.instructors.all():
                    assessment_count_instructor = Assessment.objects.filter(
                        course=course_obj, 
                        instructor=instructor
                    ).count()
                    instructors.append({
                        'id': instructor.instructor_id,
                        'name': instructor.name,
                        'specialization': instructor.specialization,
                        'assessment_count': assessment_count_instructor
                    })
                
                # Get students enrolled in this course
                students = []
                enrollments = Enrollment.objects.filter(course=course_obj)
                for enrollment in enrollments:
                    student = enrollment.student
                    students.append({
                        'id': student.student_id,
                        'name': student.name,
                        'year': student.year,
                        'gpa': student.gpa,
                        'final_grade': enrollment.final_grade or 0
                    })
                
                # Get assessment statistics
                assessment_stats = []
                assessment_types = Assessment.objects.filter(course=course_obj).values_list('type', flat=True).distinct()
                for type_name in assessment_types:
                    assessments = Assessment.objects.filter(course=course_obj, type=type_name)
                    count = assessments.count()
                    avg_score = assessments.aggregate(avg=models.Avg('score'))['avg'] or 0
                    min_score = assessments.aggregate(min=models.Min('score'))['min'] or 0
                    max_score = assessments.aggregate(max=models.Max('score'))['max'] or 0
                    
                    assessment_stats.append({
                        'type': type_name,
                        'count': count,
                        'avg_score': round(avg_score, 1),
                        'min_score': round(min_score, 1),
                        'max_score': round(max_score, 1)
                    })
                
                # Grade distribution
                grade_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
                for enrollment in enrollments:
                    if enrollment.final_grade:
                        if enrollment.final_grade >= 90:
                            grade_distribution['A'] += 1
                        elif enrollment.final_grade >= 80:
                            grade_distribution['B'] += 1
                        elif enrollment.final_grade >= 70:
                            grade_distribution['C'] += 1
                        elif enrollment.final_grade >= 60:
                            grade_distribution['D'] += 1
                        else:
                            grade_distribution['F'] += 1
                
            except Exception as e:
                # Fall back to dummy data if error occurs
                logging.warning(f"Error fetching course data: {str(e)}")
                raise Http404("Course not found")
        else:
            # Use dummy data if models are not available
            enrollment_count = random.randint(15, 40)
            assessment_count_course = random.randint(30, 100)
            
            course = {
                'id': course_id,
                'name': f'Course {course_id}',
                'code': f'CS{course_id}',
                'credits': random.randint(1, 4),
                'students': enrollment_count
            }
            
            # Dummy instructors
            instructors = []
            for i in range(1, 3):
                instructors.append({
                    'id': i,
                    'name': f'Instructor {i}',
                    'specialization': random.choice(['Algorithms', 'Machine Learning', 'Databases', 'Networking']),
                    'assessment_count': random.randint(10, 30)
                })
            
            # Dummy students
            students = []
            for i in range(1, enrollment_count + 1):
                students.append({
                    'id': i,
                    'name': f'Student {i}',
                    'year': random.randint(1, 4),
                    'gpa': round(random.uniform(2.5, 4.0), 2),
                    'final_grade': round(random.uniform(60, 100), 1)
                })
            
            # Dummy assessment stats
            assessment_stats = []
            for type_name in ['Quiz', 'Exam', 'Project', 'Homework']:
                count = random.randint(3, 10)
                avg_score = round(random.uniform(70, 90), 1)
                min_score = round(max(avg_score - 20, 0), 1)
                max_score = round(min(avg_score + 20, 100), 1)
                
                assessment_stats.append({
                    'type': type_name,
                    'count': count,
                    'avg_score': avg_score,
                    'min_score': min_score,
                    'max_score': max_score
                })
            
            # Dummy grade distribution
            grade_distribution = {
                'A': int(enrollment_count * 0.3),
                'B': int(enrollment_count * 0.4),
                'C': int(enrollment_count * 0.2),
                'D': int(enrollment_count * 0.07),
                'F': int(enrollment_count * 0.03)
            }
    
        # Get counts for sidebar statistics
        student_count = Student.objects.count() if MODELS_AVAILABLE else random.randint(50, 200)
        instructor_count = Instructor.objects.count() if MODELS_AVAILABLE else random.randint(10, 30)
        course_count = Course.objects.count() if MODELS_AVAILABLE else random.randint(20, 50)
        assessment_count = Assessment.objects.count() if MODELS_AVAILABLE else random.randint(200, 500)
        
        return render(request, 'network_simulation/course_detail.html', {
            'title': f'Course: {course["name"]}',
            'course': course,
            'instructors': instructors,
            'students': students,
            'assessment_stats': assessment_stats,
            'grade_distribution': grade_distribution,
            'enrollment_count': enrollment_count,
            'assessment_count': assessment_count_course,
            'student_count': student_count,
            'instructor_count': instructor_count,
            'course_count': course_count,
            'assessment_count': assessment_count
        })
        
    except Exception as e:
        logging.error(f"Error in course_detail view: {str(e)}")
        raise Http404("Course not found")

# API endpoints for AJAX requests

def api_course_network(request):
    """API endpoint that returns course network data in JSON format"""
    try:
        # Generate sample course network data
        nodes = []
        links = []
        
        # Create 10 course nodes
        for i in range(1, 11):
            nodes.append({
                'id': f'course_{i}',
                'name': f'Course {i}',
                'type': 'course',
                'students': random.randint(15, 40)
            })
        
        # Create connections between courses (prerequisites, related courses, etc.)
        for i in range(1, 10):
            # Each course connects to 1-3 other courses
            for _ in range(random.randint(1, 3)):
                target = random.randint(i+1, 10)
                links.append({
                    'source': f'course_{i}',
                    'target': f'course_{target}',
                    'value': random.randint(1, 5),  # Strength of relationship
                    'type': random.choice(['prerequisite', 'related', 'sequential'])
                })
        
        # Create a network visualization using NetworkX
        G = nx.Graph()
        
        # Add nodes and edges to graph
        for node in nodes:
            G.add_node(node['id'], name=node['name'], students=node['students'])
        
        for link in links:
            G.add_edge(link['source'], link['target'], weight=link['value'], type=link['type'])
        
        # Calculate network metrics
        network_metrics = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'avg_degree_centrality': sum(dict(G.degree()).values()) / len(G),
            'community_count': len(list(nx.connected_components(G)))
        }
        
        # Generate mock course data for charts
        course_enrollment = []
        for node in nodes:
            course_enrollment.append({
                'name': node['name'],
                'student_count': node['students']
            })
        
        # Generate mock course grades
        course_avg_grades = []
        for node in nodes:
            course_avg_grades.append({
                'name': node['name'],
                'avg_grade': round(random.uniform(70, 90), 1)
            })
        
        # Generate mock course connections
        course_connections = []
        for link in links:
            source_node = next(n for n in nodes if n['id'] == link['source'])
            target_node = next(n for n in nodes if n['id'] == link['target'])
            course_connections.append({
                'course1_id': link['source'].split('_')[1],
                'course1_name': source_node['name'],
                'course2_id': link['target'].split('_')[1],
                'course2_name': target_node['name'],
                'shared_students': link['value']
            })
        
        # Create a mock graph image for display
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)
        node_sizes = [nodes[i]['students']*5 for i in range(len(nodes))]
        nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color='lightblue', 
                font_size=8, edge_color='gray', width=[G[u][v]['weight']/2 for u,v in G.edges()])
        
        # Save plot to a base64 encoded image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return JsonResponse({
            'nodes': nodes, 
            'links': links,
            'network_graph': graph_image,
            'network_metrics': network_metrics,
            'course_enrollment': course_enrollment,
            'course_avg_grades': course_avg_grades,
            'course_connections': course_connections
        })
        
    except Exception as e:
        logging.error(f"Error in api_course_network: {str(e)}")
        return JsonResponse({'error': 'Error generating course network data'}, status=500)

def api_student_instructor_network(request):
    """API endpoint that returns student-instructor network data in JSON format"""
    try:
        # Generate sample student-instructor network data
        nodes = []
        links = []
        
        # Create 5 instructor nodes
        for i in range(1, 6):
            nodes.append({
                'id': f'instructor_{i}',
                'name': f'Instructor {i}',
                'type': 'instructor',
                'courses': random.randint(1, 4)
            })
            
        # Create 30 student nodes
        for i in range(1, 31):
            nodes.append({
                'id': f'student_{i}',
                'name': f'Student {i}',
                'type': 'student',
                'courses': random.randint(3, 6)
            })
        
        # Create connections between students and instructors
        for s in range(1, 31):
            # Each student connects to 2-4 instructors
            for _ in range(random.randint(2, 4)):
                instructor = random.randint(1, 5)
                links.append({
                    'source': f'student_{s}',
                    'target': f'instructor_{instructor}',
                    'value': random.randint(1, 5),  # Strength of relationship
                    'courses': random.randint(1, 3)  # Number of courses taken with this instructor
                })
        
        # Create a network visualization
        # Create sample network metrics
        network_metrics = {
            'node_count': len(nodes),
            'edge_count': len(links),
            'density': len(links) / (len(nodes) * (len(nodes) - 1) / 2),
            'avg_degree_centrality': 2 * len(links) / len(nodes),
            'community_count': random.randint(2, 5),
            'largest_component_size': len(nodes),
            'largest_component_diameter': random.randint(3, 6)
        }
        
        # Create sample instructor data
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
        
        # Create sample student data
        top_students = []
        for i in range(1, 11):
            top_students.append({
                'id': i,
                'name': f'Student {i}',
                'instructor_count': random.randint(2, 5),
                'gpa': round(random.uniform(2.5, 4.0), 2)
            })
        
        # Create a mock graph image for display
        # This is a placeholder - in a production app, we'd create a real network visualization
        G = nx.Graph()
        for node in nodes:
            G.add_node(node['id'], type=node['type'])
        for link in links:
            G.add_edge(link['source'], link['target'], weight=link['value'])
        
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G)
        node_colors = ['blue' if 'instructor' in node else 'green' for node in G.nodes()]
        nx.draw(G, pos, node_color=node_colors, with_labels=False, node_size=100, alpha=0.8, edgecolors='gray')
        
        # Save plot to a base64 encoded image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return JsonResponse({
            'nodes': nodes, 
            'links': links,
            'network_graph': graph_image, 
            'network_metrics': network_metrics,
            'top_instructors': top_instructors,
            'instructor_avg_scores': instructor_avg_scores,
            'top_students': top_students
        })
    except Exception as e:
        logging.error(f"Error in api_student_instructor_network: {str(e)}")
        return JsonResponse({'error': 'Error generating network data'}, status=500)

def api_student_performance(request):
    """API endpoint that returns student performance data in JSON format"""
    # Generate sample student performance data
    students = 20
    courses = 5
    
    # Performance data over time
    time_data = {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        'datasets': []
    }
    
    # Generate performance data for each course
    for c in range(1, courses + 1):
        time_data['datasets'].append({
            'label': f'Course {c}',
            'data': [round(random.uniform(60, 95), 1) for _ in range(8)],
            'borderColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)',
            'fill': False
        })
    
    # Distribution of grades
    grade_distribution = {
        'labels': ['A', 'B', 'C', 'D', 'F'],
        'datasets': [{
            'label': 'Grade Distribution',
            'data': [
                random.randint(5, 15),   # A
                random.randint(15, 25),  # B
                random.randint(20, 30),  # C
                random.randint(5, 15),   # D
                random.randint(1, 10)    # F
            ],
            'backgroundColor': [
                'rgba(75, 192, 192, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(255, 159, 64, 0.6)',
                'rgba(255, 99, 132, 0.6)'
            ]
        }]
    }
    
    # Top performing students
    top_students = []
    for i in range(1, 11):
        top_students.append({
            'id': i,
            'name': f'Student {i}',
            'average': round(random.uniform(85, 99), 2),
            'courses': random.randint(3, 5)
        })
    
    # Sort by average score
    top_students.sort(key=lambda x: x['average'], reverse=True)
    
    return JsonResponse({
        'time_data': time_data,
        'grade_distribution': grade_distribution,
        'top_students': top_students
    })

# New dashboard views for role-based analytics

def student_analytics_dashboard(request):
    """Student dashboard for viewing analytics about their own performance"""
    # Get student user ID - this assumes the user ID in the session is valid
    student_id = request.session.get('user_id')
    
    if not student_id:
        return redirect('/')
    
    # Check if user is a student
    users = db.collection('users')
    user = users.get(student_id)
    
    if not user or user.get('role') != 'student':
        return redirect('/')
    
    # Get student's mistake history
    mistakes = get_student_mistakes(student_id)
    
    # Get student's weakest areas
    weak_areas = get_student_weakest_areas(student_id)
    
    # Get recommended sections
    recommended_sections = get_section_recommendations(student_id)
    
    context = {
        'student_id': student_id,
        'student_name': user.get('username', 'Student'),
        'mistakes': mistakes,
        'weak_areas': weak_areas,
        'recommended_sections': recommended_sections
    }
    
    return render(request, 'network_simulation/student_dashboard.html', context)

def instructor_analytics_dashboard(request):
    """Instructor dashboard for viewing analytics about student performance"""
    # Get instructor user ID
    instructor_id = request.session.get('user_id')
    
    if not instructor_id:
        return redirect('/')
    
    # Check if user is an instructor
    users = db.collection('users')
    user = users.get(instructor_id)
    
    if not user or user.get('role') != 'instructor':
        return redirect('/')
    
    # Get mistake heatmap data
    heatmap = get_instructor_mistake_heatmap(instructor_id)
    
    # Get top common mistakes
    common_mistakes = get_top_common_mistakes(instructor_id)
    most_common_count = common_mistakes[0]['count'] if common_mistakes else 0
    
    # Get potential grading inconsistencies
    inconsistencies = detect_grading_inconsistencies(instructor_id)
    
    # Get mistake clusters
    mistake_clusters = get_mistake_clusters_with_stats()
    
    context = {
        'instructor_id': instructor_id,
        'instructor_name': user.get('username', 'Instructor'),
        'heatmap': heatmap,
        'common_mistakes': common_mistakes,
        'most_common_count': most_common_count,
        'inconsistencies': inconsistencies,
        'mistake_clusters': mistake_clusters
    }
    
    return render(request, 'network_simulation/instructor_dashboard.html', context)

def api_section_detail(request, section_id):
    """API endpoint to get a section's details"""
    try:
        sections = db.collection('sections')
        section = sections.get(section_id)
        
        if not section:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        return JsonResponse({
            'id': section['_id'],
            'title': section.get('title', 'No Title'),
            'class_code': section.get('class_code', ''),
            'content': section.get('content', 'No content available')
        })
    except Exception as e:
        logging.error(f"Error getting section details: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def api_mistake_clusters(request):
    """API endpoint to get mistake clusters for visualization"""
    try:
        clusters = get_mistake_clusters_with_stats()
        return JsonResponse(clusters)
    except Exception as e:
        logging.error(f"Error getting mistake clusters: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def api_student_mistakes(request, student_id):
    """API endpoint to get a student's mistakes"""
    try:
        # Check if user has permission to view this student's mistakes
        current_user_id = request.session.get('user_id')
        users = db.collection('users')
        user = users.get(current_user_id)
        
        # Only allow instructors or the student themselves to view their mistakes
        if not user or (user.get('role') != 'instructor' and str(current_user_id) != str(student_id)):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        mistakes = get_student_mistakes(student_id)
        return JsonResponse({
            'student_id': student_id,
            'mistakes': mistakes
        })
    except Exception as e:
        logging.error(f"Error getting student mistakes: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def api_instructor_mistake_heatmap(request, instructor_id):
    """API endpoint to get instructor mistake heatmap data"""
    try:
        # Check if user has permission to view this instructor's heatmap
        current_user_id = request.session.get('user_id')
        users = db.collection('users')
        user = users.get(current_user_id)
        
        # Only allow instructors to view their own heatmap
        if not user or user.get('role') != 'instructor' or str(current_user_id) != str(instructor_id):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        heatmap = get_instructor_mistake_heatmap(instructor_id)
        return JsonResponse({
            'instructor_id': instructor_id,
            'heatmap': heatmap
        })
    except Exception as e:
        logging.error(f"Error getting instructor mistake heatmap: {e}")
        return JsonResponse({'error': str(e)}, status=500)