import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Count, Avg, Max, Min
from .models import Student, Instructor, Course, Enrollment, Assessment

def build_student_instructor_network():
    """
    Build a bipartite network of students and instructors based on assessments.
    Returns a NetworkX graph object.
    """
    G = nx.Graph()
    
    # Add all students as nodes
    for student in Student.objects.all():
        G.add_node(student.student_id, 
                  type='student', 
                  name=student.name, 
                  year=student.year, 
                  gpa=student.gpa)
    
    # Add all instructors as nodes
    for instructor in Instructor.objects.all():
        G.add_node(instructor.instructor_id, 
                  type='instructor', 
                  name=instructor.name, 
                  department=instructor.department,
                  specialization=instructor.specialization)
    
    # Add edges based on assessments
    for assessment in Assessment.objects.all():
        # Create an edge between student and instructor
        edge_key = (assessment.student.student_id, assessment.instructor.instructor_id)
        
        # If edge already exists, update the weight
        if G.has_edge(*edge_key):
            # Increment the assessment count
            G.edges[edge_key]['count'] += 1
            # Update the average score
            total_score = G.edges[edge_key]['avg_score'] * G.edges[edge_key]['count']
            new_avg = (total_score + assessment.score) / (G.edges[edge_key]['count'] + 1)
            G.edges[edge_key]['avg_score'] = new_avg
        else:
            # Create a new edge with weight based on assessment
            G.add_edge(
                assessment.student.student_id,
                assessment.instructor.instructor_id,
                count=1,
                avg_score=assessment.score,
                course_id=assessment.course.course_id
            )
    
    return G

def build_course_network():
    """
    Build a network of courses connected when they share students.
    Returns a NetworkX graph object.
    """
    G = nx.Graph()
    
    # Add all courses as nodes
    for course in Course.objects.all():
        G.add_node(course.course_id, 
                  name=course.name, 
                  credits=course.credits)
    
    # Find pairs of courses that share students
    course_pairs = {}
    
    # For each student, look at all pairs of courses they're enrolled in
    for student in Student.objects.all():
        courses = list(Enrollment.objects.filter(student=student).values_list('course__course_id', flat=True))
        
        # For each pair of courses
        for i, course1 in enumerate(courses):
            for course2 in courses[i+1:]:
                pair = tuple(sorted([course1, course2]))
                
                if pair in course_pairs:
                    course_pairs[pair] += 1
                else:
                    course_pairs[pair] = 1
    
    # Add edges to the network
    for (course1, course2), weight in course_pairs.items():
        G.add_edge(course1, course2, weight=weight, shared_students=weight)
    
    return G

def calculate_network_metrics(G):
    """
    Calculate key network metrics for a given graph.
    Returns a dictionary of metrics.
    """
    metrics = {}
    
    # Basic network metrics
    metrics['node_count'] = G.number_of_nodes()
    metrics['edge_count'] = G.number_of_edges()
    metrics['density'] = nx.density(G)
    
    # Only calculate these if the graph is connected
    if nx.is_connected(G):
        metrics['diameter'] = nx.diameter(G)
        metrics['average_shortest_path'] = nx.average_shortest_path_length(G)
    else:
        # Get largest connected component metrics
        largest_cc = max(nx.connected_components(G), key=len)
        subgraph = G.subgraph(largest_cc)
        metrics['largest_component_size'] = len(largest_cc)
        metrics['largest_component_diameter'] = nx.diameter(subgraph)
        metrics['largest_component_avg_path'] = nx.average_shortest_path_length(subgraph)
    
    # Centrality measures
    degree_centrality = nx.degree_centrality(G)
    metrics['avg_degree_centrality'] = sum(degree_centrality.values()) / len(degree_centrality)
    metrics['max_degree_centrality'] = max(degree_centrality.items(), key=lambda x: x[1])
    
    try:
        betweenness_centrality = nx.betweenness_centrality(G)
        metrics['avg_betweenness_centrality'] = sum(betweenness_centrality.values()) / len(betweenness_centrality)
        metrics['max_betweenness_centrality'] = max(betweenness_centrality.items(), key=lambda x: x[1])
    except:
        # Skip if there's an issue with betweenness calculation
        metrics['avg_betweenness_centrality'] = 'N/A'
        metrics['max_betweenness_centrality'] = 'N/A'
    
    # Community detection (using Louvain method if available)
    try:
        from community import best_partition
        partition = best_partition(G)
        metrics['community_count'] = len(set(partition.values()))
        metrics['modularity'] = nx.community.modularity(G, partition.values())
    except ImportError:
        # Fall back to connected components if community detection is not available
        components = list(nx.connected_components(G))
        metrics['community_count'] = len(components)
        metrics['modularity'] = 'N/A (community package not available)'
    
    return metrics

def render_network_graph(G, title, node_attr=None, layout=nx.spring_layout, figsize=(10, 8)):
    """
    Render a network graph visualization.
    Returns the plot as a base64 encoded string.
    """
    plt.figure(figsize=figsize)
    plt.title(title)
    
    # Set up node colors based on attributes if provided
    if node_attr:
        node_colors = []
        for node in G.nodes():
            if node_attr in G.nodes[node]:
                if G.nodes[node][node_attr] == 'student':
                    node_colors.append('skyblue')
                elif G.nodes[node][node_attr] == 'instructor':
                    node_colors.append('salmon')
                else:
                    node_colors.append('lightgray')
            else:
                node_colors.append('lightgray')
    else:
        node_colors = 'lightblue'
    
    # Calculate edge widths based on weights if available
    edge_widths = []
    for u, v, data in G.edges(data=True):
        if 'weight' in data:
            edge_widths.append(data['weight'] * 0.5)  # Scale down for better visualization
        elif 'avg_score' in data:
            edge_widths.append(data['count'] * 0.5)  # Use count as a proxy for weight
        else:
            edge_widths.append(1.0)
    
    # Create network layout
    pos = layout(G)
    
    # Draw the network
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    # Save the plot to a buffer
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    
    # Encode the image to base64
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def get_student_instructor_analytics():
    """
    Get analytics for student-instructor relationships.
    Returns a dictionary of analytics.
    """
    analytics = {}
    
    # Build the network
    G = build_student_instructor_network()
    
    # Calculate network metrics
    analytics['network_metrics'] = calculate_network_metrics(G)
    
    # Get top instructors by number of students
    instructors = Instructor.objects.annotate(
        student_count=Count('assessments__student', distinct=True)
    ).order_by('-student_count')[:5]
    
    analytics['top_instructors'] = [
        {
            'id': instructor.instructor_id,
            'name': instructor.name,
            'student_count': instructor.student_count
        }
        for instructor in instructors
    ]
    
    # Get students with most instructor interactions
    students = Student.objects.annotate(
        instructor_count=Count('assessments__instructor', distinct=True)
    ).order_by('-instructor_count')[:5]
    
    analytics['top_students'] = [
        {
            'id': student.student_id,
            'name': student.name,
            'instructor_count': student.instructor_count
        }
        for student in students
    ]
    
    # Get average scores by instructor
    instructor_scores = []
    for instructor in Instructor.objects.all():
        avg_score = Assessment.objects.filter(instructor=instructor).aggregate(Avg('score'))['score__avg']
        if avg_score:
            instructor_scores.append({
                'id': instructor.instructor_id,
                'name': instructor.name,
                'avg_score': round(avg_score, 2)
            })
    
    # Sort by average score
    instructor_scores.sort(key=lambda x: x['avg_score'], reverse=True)
    analytics['instructor_avg_scores'] = instructor_scores[:5]
    
    # Render network visualization
    analytics['network_graph'] = render_network_graph(
        G, 'Student-Instructor Network', node_attr='type'
    )
    
    return analytics

def get_course_analytics():
    """
    Get analytics for course relationships.
    Returns a dictionary of analytics.
    """
    analytics = {}
    
    # Build the network
    G = build_course_network()
    
    # Calculate network metrics
    analytics['network_metrics'] = calculate_network_metrics(G)
    
    # Get courses with most students
    courses = Course.objects.annotate(
        student_count=Count('enrollments__student', distinct=True)
    ).order_by('-student_count')
    
    analytics['course_enrollment'] = [
        {
            'id': course.course_id,
            'name': course.name,
            'student_count': course.student_count
        }
        for course in courses
    ]
    
    # Get average grades by course
    course_grades = []
    for course in Course.objects.all():
        avg_grade = Enrollment.objects.filter(
            course=course,
            final_grade__isnull=False
        ).aggregate(Avg('final_grade'))['final_grade__avg']
        
        if avg_grade:
            course_grades.append({
                'id': course.course_id,
                'name': course.name,
                'avg_grade': round(avg_grade, 2)
            })
    
    # Sort by average grade
    course_grades.sort(key=lambda x: x['avg_grade'], reverse=True)
    analytics['course_avg_grades'] = course_grades
    
    # Get course pairs with most shared students
    course_connections = []
    for (course1, course2, data) in G.edges(data=True):
        if 'shared_students' in data:
            course_connections.append({
                'course1_id': course1,
                'course1_name': Course.objects.get(course_id=course1).name,
                'course2_id': course2,
                'course2_name': Course.objects.get(course_id=course2).name,
                'shared_students': data['shared_students']
            })
    
    # Sort by number of shared students
    course_connections.sort(key=lambda x: x['shared_students'], reverse=True)
    analytics['course_connections'] = course_connections[:10]
    
    # Render network visualization
    analytics['network_graph'] = render_network_graph(
        G, 'Course Relationship Network'
    )
    
    return analytics

def get_student_performance_analytics():
    """
    Get analytics for student performance across courses.
    Returns a dictionary of analytics.
    """
    analytics = {}
    
    # Get overall GPA distribution
    students = Student.objects.all()
    gpa_values = [student.gpa for student in students]
    
    analytics['gpa_stats'] = {
        'min': min(gpa_values),
        'max': max(gpa_values),
        'mean': sum(gpa_values) / len(gpa_values) if gpa_values else 0,
        'quartiles': np.percentile(gpa_values, [25, 50, 75]).tolist() if gpa_values else [0, 0, 0]
    }
    
    # Get grade distribution by course
    course_grades = {}
    for course in Course.objects.all():
        grades = list(Enrollment.objects.filter(
            course=course,
            final_grade__isnull=False
        ).values_list('final_grade', flat=True))
        
        if grades:
            course_grades[course.name] = {
                'min': min(grades),
                'max': max(grades),
                'mean': sum(grades) / len(grades),
                'count': len(grades),
                'distribution': {
                    'A': sum(1 for g in grades if g >= 90),
                    'B': sum(1 for g in grades if 80 <= g < 90),
                    'C': sum(1 for g in grades if 70 <= g < 80),
                    'D': sum(1 for g in grades if 60 <= g < 70),
                    'F': sum(1 for g in grades if g < 60)
                }
            }
    
    analytics['course_grade_stats'] = course_grades
    
    # Get top performing students
    top_students = Student.objects.order_by('-gpa')[:10]
    analytics['top_students'] = [
        {
            'id': student.student_id,
            'name': student.name,
            'gpa': student.gpa,
            'year': student.year
        }
        for student in top_students
    ]
    
    # Get assessment performance by type
    assessment_types = Assessment.objects.values_list('type', flat=True).distinct()
    type_performance = {}
    
    for assessment_type in assessment_types:
        scores = list(Assessment.objects.filter(type=assessment_type).values_list('score', flat=True))
        if scores:
            type_performance[assessment_type] = {
                'min': min(scores),
                'max': max(scores),
                'mean': sum(scores) / len(scores),
                'count': len(scores)
            }
    
    analytics['assessment_type_stats'] = type_performance
    
    return analytics
