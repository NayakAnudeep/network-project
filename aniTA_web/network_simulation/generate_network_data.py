"""
One-time script to generate network data and store it in the database.

Run this script with:
python manage.py shell < network_simulation/generate_network_data.py
"""

import os
import django
import random
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import networkx as nx

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from network_simulation.models import NetworkData

def generate_student_instructor_network():
    """Generate student-instructor network data and save to database."""
    print("Generating student-instructor network data...")
    
    # Generate sample nodes and links
    nodes = []
    links = []
    
    # Create instructor nodes
    instructor_count = 5
    for i in range(1, instructor_count + 1):
        nodes.append({
            'id': f'instructor_{i}',
            'name': f'Professor {i}',
            'type': 'instructor',
            'courses': random.randint(1, 4)
        })
    
    # Create student nodes
    student_count = 30
    for i in range(1, student_count + 1):
        nodes.append({
            'id': f'student_{i}',
            'name': f'Student {i}',
            'type': 'student',
            'courses': random.randint(3, 6)
        })
    
    # Create connections between students and instructors
    for s in range(1, student_count + 1):
        # Each student connects to 2-4 instructors
        instructor_connections = random.sample(range(1, instructor_count + 1), random.randint(2, 4))
        for instructor in instructor_connections:
            links.append({
                'source': f'student_{s}',
                'target': f'instructor_{instructor}',
                'value': random.randint(1, 5),  # Strength of relationship
                'courses': random.randint(1, 3),  # Number of courses with this instructor
                'grade': round(random.uniform(70, 95), 1)  # Average grade
            })
    
    # Create a network visualization
    G = nx.Graph()
    for node in nodes:
        G.add_node(node['id'], type=node['type'])
    
    for link in links:
        G.add_edge(link['source'], link['target'], weight=link['value'])
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Seed for reproducibility
    
    # Color nodes by type
    node_colors = ['blue' if 'instructor' in node_id else 'green' for node_id in G.nodes()]
    
    # Draw the network
    nx.draw(G, pos, node_color=node_colors, with_labels=False, 
            node_size=100, alpha=0.8, edgecolors='gray')
    
    # Save plot to a base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    # Calculate network metrics
    network_metrics = {
        'node_count': len(nodes),
        'edge_count': len(links),
        'density': len(links) / (len(nodes) * (len(nodes) - 1) / 2),
        'avg_degree_centrality': 2 * len(links) / len(nodes),
        'avg_betweenness_centrality': 0.03,  # Placeholder
        'community_count': 5,  # Placeholder
        'largest_component_size': len(nodes),
        'largest_component_diameter': 6,  # Placeholder
        'modularity': 0.52  # Placeholder
    }
    
    # Generate top instructors by student connections
    top_instructors = []
    instructor_connections = {}
    
    for link in links:
        if 'instructor' in link['target']:
            instructor_connections[link['target']] = instructor_connections.get(link['target'], 0) + 1
        elif 'instructor' in link['source']:
            instructor_connections[link['source']] = instructor_connections.get(link['source'], 0) + 1
    
    for i in range(1, instructor_count + 1):
        instructor_id = f'instructor_{i}'
        top_instructors.append({
            'id': i,
            'name': f'Professor {i}',
            'student_count': instructor_connections.get(instructor_id, 0)
        })
    
    # Sort by student count
    top_instructors.sort(key=lambda x: x['student_count'], reverse=True)
    
    # Generate instructor average scores
    instructor_avg_scores = []
    
    for i in range(1, instructor_count + 1):
        instructor_id = f'instructor_{i}'
        instructor_grades = [link['grade'] for link in links if link['target'] == instructor_id or link['source'] == instructor_id]
        avg_score = sum(instructor_grades) / len(instructor_grades) if instructor_grades else 85.0
        
        instructor_avg_scores.append({
            'id': i,
            'name': f'Professor {i}',
            'avg_score': round(avg_score, 1)
        })
    
    # Generate top students
    top_students = []
    student_connections = {}
    
    for link in links:
        if 'student' in link['source']:
            student_connections[link['source']] = student_connections.get(link['source'], 0) + 1
        elif 'student' in link['target']:
            student_connections[link['target']] = student_connections.get(link['target'], 0) + 1
    
    for i in range(1, student_count + 1):
        student_id = f'student_{i}'
        if student_id in student_connections:
            top_students.append({
                'id': i,
                'name': f'Student {i}',
                'instructor_count': student_connections[student_id],
                'gpa': round(random.uniform(2.8, 4.0), 2)
            })
    
    # Sort by instructor count
    top_students.sort(key=lambda x: x['instructor_count'], reverse=True)
    top_students = top_students[:10]  # Take top 10
    
    # Compile final data
    network_data = {
        'nodes': nodes,
        'links': links,
        'network_graph': graph_image,
        'network_metrics': network_metrics,
        'top_instructors': top_instructors,
        'instructor_avg_scores': instructor_avg_scores,
        'top_students': top_students
    }
    
    # Save to database
    try:
        network_record = NetworkData.objects.get(name='student_instructor_network')
        print("Updating existing student-instructor network data...")
    except NetworkData.DoesNotExist:
        network_record = NetworkData(name='student_instructor_network', data_type='student_instructor_network')
        print("Creating new student-instructor network data...")
    
    network_record.set_data(network_data)
    network_record.save()
    
    print("Student-instructor network data saved successfully.")
    return network_data

def generate_course_network():
    """Generate course network data and save to database."""
    print("Generating course network data...")
    
    # Generate nodes (courses)
    nodes = []
    course_count = 10
    
    for i in range(1, course_count + 1):
        nodes.append({
            'id': f'course_{i}',
            'name': f'Course {i}',
            'type': 'course',
            'students': random.randint(15, 50)
        })
    
    # Generate links (connections between courses)
    links = []
    
    # Create connections (shared students between courses)
    for i in range(course_count):
        for j in range(i+1, course_count):
            # About 30% chance of connection between any two courses
            if random.random() < 0.3:
                links.append({
                    'source': i,
                    'target': j,
                    'weight': random.randint(1, 15)  # Number of shared students
                })
    
    # Create a network visualization
    G = nx.Graph()
    
    # Add nodes to the graph
    for i, node in enumerate(nodes):
        G.add_node(i, name=node['name'], students=node['students'])
    
    # Add edges to the graph
    for link in links:
        G.add_edge(link['source'], link['target'], weight=link['weight'])
    
    # Calculate network metrics
    network_metrics = {
        'node_count': G.number_of_nodes(),
        'edge_count': G.number_of_edges(),
        'density': nx.density(G),
        'avg_degree_centrality': sum(dict(G.degree()).values()) / len(G),
        'community_count': len(list(nx.connected_components(G))),
        'diameter': nx.diameter(G) if nx.is_connected(G) else 'N/A (not a connected graph)',
        'average_shortest_path': nx.average_shortest_path_length(G) if nx.is_connected(G) else 'N/A'
    }
    
    # Create visualization
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Seed for reproducibility
    
    # Node sizes based on student count
    node_sizes = [nodes[i]['students'] * 5 for i in range(len(nodes))]
    
    # Edge widths based on weight (shared students)
    edge_widths = [G[u][v]['weight'] / 2 for u, v in G.edges()]
    
    # Draw the network
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, 
            node_color='lightblue', font_size=8, edge_color='gray', 
            width=edge_widths)
    
    # Save plot to a base64 encoded image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    # Generate mock course enrollment data
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
        course_connections.append({
            'course1_id': nodes[link['source']]['id'].split('_')[1],
            'course1_name': nodes[link['source']]['name'],
            'course2_id': nodes[link['target']]['id'].split('_')[1],
            'course2_name': nodes[link['target']]['name'],
            'shared_students': link['weight']
        })
    
    # Compile final data
    network_data = {
        'nodes': nodes,
        'links': links,
        'network_graph': graph_image,
        'network_metrics': network_metrics,
        'course_enrollment': course_enrollment,
        'course_avg_grades': course_avg_grades,
        'course_connections': course_connections
    }
    
    # Save to database
    try:
        network_record = NetworkData.objects.get(name='course_network')
        print("Updating existing course network data...")
    except NetworkData.DoesNotExist:
        network_record = NetworkData(name='course_network', data_type='course_network')
        print("Creating new course network data...")
    
    network_record.set_data(network_data)
    network_record.save()
    
    print("Course network data saved successfully.")
    return network_data

def generate_student_performance_data():
    """Generate student performance data and save to database."""
    print("Generating student performance data...")
    
    # GPA statistics
    gpa_stats = {
        'min': 2.0,
        'max': 4.0,
        'mean': 3.2,
        'median': 3.3,
        'distribution': {
            '2.0-2.5': 15,
            '2.5-3.0': 25,
            '3.0-3.5': 35,
            '3.5-4.0': 25
        }
    }
    
    # Course grade statistics
    course_grade_stats = {}
    for c in range(1, 6):
        course_name = f'Course {c}'
        course_grade_stats[course_name] = {
            'mean': round(random.uniform(70, 85), 2),
            'median': round(random.uniform(70, 85), 2),
            'min': round(random.uniform(50, 65), 2),
            'max': round(random.uniform(85, 98), 2),
            'distribution': {
                'A': random.randint(5, 15),
                'B': random.randint(15, 25),
                'C': random.randint(20, 30),
                'D': random.randint(5, 15),
                'F': random.randint(1, 10)
            }
        }
    
    # Assessment type statistics
    assessment_type_stats = {
        'Quiz': {
            'mean': round(random.uniform(70, 85), 2),
            'median': round(random.uniform(70, 85), 2),
            'min': round(random.uniform(50, 65), 2),
            'max': round(random.uniform(85, 98), 2),
            'count': random.randint(10, 30)
        },
        'Exam': {
            'mean': round(random.uniform(70, 85), 2),
            'median': round(random.uniform(70, 85), 2),
            'min': round(random.uniform(50, 65), 2),
            'max': round(random.uniform(85, 98), 2),
            'count': random.randint(5, 15)
        },
        'Project': {
            'mean': round(random.uniform(75, 90), 2),
            'median': round(random.uniform(75, 90), 2),
            'min': round(random.uniform(60, 75), 2),
            'max': round(random.uniform(90, 100), 2),
            'count': random.randint(3, 8)
        },
        'Homework': {
            'mean': round(random.uniform(80, 95), 2),
            'median': round(random.uniform(80, 95), 2),
            'min': round(random.uniform(65, 80), 2),
            'max': round(random.uniform(90, 100), 2),
            'count': random.randint(15, 25)
        }
    }
    
    # Top performing students
    top_students = []
    for i in range(1, 11):
        top_students.append({
            'id': i,
            'name': f'Student {i}',
            'year': random.randint(1, 4),
            'gpa': round(random.uniform(3.0, 4.0), 2),
            'courses': random.randint(3, 5)
        })
    
    # Sort by GPA
    top_students.sort(key=lambda x: x['gpa'], reverse=True)
    
    # Performance data over time
    time_data = {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
        'datasets': []
    }
    
    # Generate performance data for each course
    for c in range(1, 6):
        time_data['datasets'].append({
            'label': f'Course {c}',
            'data': [round(random.uniform(60, 95), 1) for _ in range(8)],
            'borderColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)',
            'fill': False
        })
    
    # Compile final data
    performance_data = {
        'gpa_stats': gpa_stats,
        'course_grade_stats': course_grade_stats,
        'assessment_type_stats': assessment_type_stats,
        'top_students': top_students,
        'time_data': time_data
    }
    
    # Save to database
    try:
        network_record = NetworkData.objects.get(name='student_performance')
        print("Updating existing student performance data...")
    except NetworkData.DoesNotExist:
        network_record = NetworkData(name='student_performance', data_type='student_performance')
        print("Creating new student performance data...")
    
    network_record.set_data(performance_data)
    network_record.save()
    
    print("Student performance data saved successfully.")
    return performance_data

if __name__ == "__main__":
    # Generate all data
    student_instructor_data = generate_student_instructor_network()
    course_network_data = generate_course_network()
    student_performance_data = generate_student_performance_data()
    
    print("All network data generated and stored successfully.")