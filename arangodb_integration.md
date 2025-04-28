# ArangoDB Network Integration Implementation

## Overview

This document outlines the steps to integrate the network simulation data with ArangoDB as a graph database. The implementation will:

1. Generate simulated users with famous people's names
2. Store all network entities in ArangoDB
3. Create proper graph relationships
4. Utilize ArangoDB for network analysis algorithms

## 1. Data Generation Enhancement

### Famous People Dataset

Create a new list of famous people names in `generate_data.py`:

```python
# Famous scientists, artists, inventors, and other notable figures
FAMOUS_FIRST_NAMES = [
    "Albert", "Marie", "Nikola", "Ada", "Leonardo", "Frida", "Isaac", "Grace",
    "Stephen", "Maya", "Wolfgang", "Jane", "Richard", "Emmy", "Charles", "Rosalind",
    "Alan", "Katherine", "Neil", "Hedy", "Thomas", "Margaret", "Carl", "Rachel",
    "Louis", "Virginia", "Max", "Toni", "Galileo", "Florence", "Alexander", "Rosa",
    "Srinivasa", "Marie", "Ernest", "Barbara", "Johannes", "Georgia", "James", "Dorothy",
    "Niels", "Sylvia", "Werner", "Zora", "Enrico", "Mary", "Robert", "Elizabeth"
]

FAMOUS_LAST_NAMES = [
    "Einstein", "Curie", "Tesla", "Lovelace", "da Vinci", "Kahlo", "Newton", "Hopper",
    "Hawking", "Angelou", "Mozart", "Austen", "Feynman", "Noether", "Darwin", "Franklin",
    "Turing", "Johnson", "Armstrong", "Lamarr", "Edison", "Mead", "Sagan", "Carson",
    "Pasteur", "Woolf", "Planck", "Morrison", "Galilei", "Nightingale", "Graham", "Parks",
    "Ramanujan", "Thatcher", "Hemingway", "McClintock", "Kepler", "O'Keeffe", "Watson", "Hodgkin",
    "Bohr", "Plath", "Heisenberg", "Hurston", "Fermi", "Shelley", "Oppenheimer", "Blackwell"
]
```

### Updated User Generation

Modify `generate_data.py` to create CSV files with famous names and credentials:

```python
def save_user_credentials_csv(data, output_dir):
    """Save user credentials as CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Student credentials
    with open(os.path.join(output_dir, 'student_credentials.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'password', 'role'])
        for student in data['students']:
            # Create email from name
            email = f"{student['name'].replace(' ', '.').lower()}@student.edu"
            writer.writerow([
                student['id'], 
                student['name'], 
                email,
                f"pass_{student['id']}", # Simple password for demo
                "student"
            ])
    
    # Instructor credentials
    with open(os.path.join(output_dir, 'instructor_credentials.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'password', 'role'])
        for instructor in data['instructors']:
            # Create email from name
            email = f"{instructor['name'].replace(' ', '.').lower()}@faculty.edu"
            writer.writerow([
                instructor['id'], 
                instructor['name'], 
                email,
                f"pass_{instructor['id']}", # Simple password for demo
                "instructor"
            ])
```

Modify the name generation to use famous names:

```python
def generate_random_name():
    return f"{random.choice(FAMOUS_FIRST_NAMES)} {random.choice(FAMOUS_LAST_NAMES)}"
```

## 2. ArangoDB Schema Enhancement

Create a new file `network_simulation/arangodb_schema.py`:

```python
from users.arangodb import db

def setup_arangodb_network_schema():
    """
    Set up the ArangoDB collections needed for the network simulation.
    """
    # Vertex collections
    if not db.has_collection('network_students'):
        db.create_collection('network_students')
    
    if not db.has_collection('network_instructors'):
        db.create_collection('network_instructors')
    
    if not db.has_collection('network_courses'):
        db.create_collection('network_courses')
    
    if not db.has_collection('network_assessments'):
        db.create_collection('network_assessments')
    
    # Edge collections
    if not db.has_collection('network_teaches'):
        db.create_collection('network_teaches', edge=True)
    
    if not db.has_collection('network_enrolled_in'):
        db.create_collection('network_enrolled_in', edge=True)
    
    if not db.has_collection('network_assessed_by'):
        db.create_collection('network_assessed_by', edge=True)
    
    if not db.has_collection('network_part_of'):
        db.create_collection('network_part_of', edge=True)
    
    print("ArangoDB network schema set up successfully")
```

## 3. Data Import to ArangoDB

Create a new file `network_simulation/import_to_arango.py`:

```python
import os
import csv
import json
from datetime import datetime
from users.arangodb import db, register_user
from .arangodb_schema import setup_arangodb_network_schema

def import_network_to_arango(json_file, csv_dir):
    """
    Import network data from JSON and user credentials from CSV to ArangoDB.
    
    Parameters:
    - json_file: Path to the network data JSON file
    - csv_dir: Directory containing student_credentials.csv and instructor_credentials.csv
    """
    # Set up the schema first
    setup_arangodb_network_schema()
    
    # Load network data
    with open(json_file, 'r') as f:
        network_data = json.load(f)
    
    # Load credentials
    student_credentials = {}
    instructor_credentials = {}
    
    with open(os.path.join(csv_dir, 'student_credentials.csv'), 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_credentials[row['id']] = row
    
    with open(os.path.join(csv_dir, 'instructor_credentials.csv'), 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            instructor_credentials[row['id']] = row
    
    # Import students
    network_students = db.collection('network_students')
    for student_data in network_data['students']:
        student_id = student_data['id']
        
        # Skip if already exists
        if list(network_students.find({'student_id': student_id})):
            continue
        
        # Create student document
        student_doc = {
            'student_id': student_id,
            'name': student_data['name'],
            'year': student_data['year'],
            'major': student_data['major'],
            'gpa': student_data['gpa'],
            'created_at': datetime.utcnow().isoformat()
        }
        student_arangodb_id = network_students.insert(student_doc)['_id']
        
        # Register user if credentials exist
        if student_id in student_credentials:
            cred = student_credentials[student_id]
            register_user(
                username=cred['name'],
                email=cred['email'],
                password=cred['password'],
                role='student'
            )
    
    # Import instructors
    network_instructors = db.collection('network_instructors')
    for instructor_data in network_data['instructors']:
        instructor_id = instructor_data['id']
        
        # Skip if already exists
        if list(network_instructors.find({'instructor_id': instructor_id})):
            continue
        
        # Create instructor document
        instructor_doc = {
            'instructor_id': instructor_id,
            'name': instructor_data['name'],
            'department': instructor_data['department'],
            'specialization': instructor_data['specialization'],
            'created_at': datetime.utcnow().isoformat()
        }
        instructor_arangodb_id = network_instructors.insert(instructor_doc)['_id']
        
        # Register user if credentials exist
        if instructor_id in instructor_credentials:
            cred = instructor_credentials[instructor_id]
            register_user(
                username=cred['name'],
                email=cred['email'],
                password=cred['password'],
                role='instructor'
            )
    
    # Import courses
    network_courses = db.collection('network_courses')
    for course_data in network_data['courses']:
        course_id = course_data['id']
        
        # Skip if already exists
        if list(network_courses.find({'course_id': course_id})):
            continue
        
        # Create course document
        course_doc = {
            'course_id': course_id,
            'name': course_data['name'],
            'credits': course_data['credits'],
            'created_at': datetime.utcnow().isoformat()
        }
        course_arangodb_id = network_courses.insert(course_doc)['_id']
        
        # Create teaches edges
        network_teaches = db.collection('network_teaches')
        for instructor_id in course_data['instructor_ids']:
            instructor_docs = list(network_instructors.find({'instructor_id': instructor_id}))
            if instructor_docs:
                instructor_arangodb_id = instructor_docs[0]['_id']
                # Create edge from instructor to course
                network_teaches.insert({
                    '_from': instructor_arangodb_id,
                    '_to': course_arangodb_id,
                    'created_at': datetime.utcnow().isoformat()
                })
    
    # Import enrollments
    network_enrolled_in = db.collection('network_enrolled_in')
    for enrollment_data in network_data['enrollments']:
        student_id = enrollment_data['student_id']
        course_id = enrollment_data['course_id']
        
        student_docs = list(network_students.find({'student_id': student_id}))
        course_docs = list(network_courses.find({'course_id': course_id}))
        
        if student_docs and course_docs:
            student_arangodb_id = student_docs[0]['_id']
            course_arangodb_id = course_docs[0]['_id']
            
            # Check if edge already exists
            existing_edges = list(network_enrolled_in.find({
                '_from': student_arangodb_id,
                '_to': course_arangodb_id
            }))
            
            if not existing_edges:
                # Create enrollment edge
                network_enrolled_in.insert({
                    '_from': student_arangodb_id,
                    '_to': course_arangodb_id,
                    'term': enrollment_data['term'],
                    'year': enrollment_data['year'],
                    'final_grade': enrollment_data['final_grade'],
                    'created_at': datetime.utcnow().isoformat()
                })
    
    # Import assessments
    network_assessments = db.collection('network_assessments')
    network_assessed_by = db.collection('network_assessed_by')
    network_part_of = db.collection('network_part_of')
    
    for assessment_data in network_data['assessments']:
        assessment_id = assessment_data['id']
        
        # Skip if already exists
        if list(network_assessments.find({'assessment_id': assessment_id})):
            continue
        
        # Create assessment document
        assessment_doc = {
            'assessment_id': assessment_id,
            'student_id': assessment_data['student_id'],
            'course_id': assessment_data['course_id'],
            'instructor_id': assessment_data['instructor_id'],
            'term': assessment_data['term'],
            'year': assessment_data['year'],
            'type': assessment_data['type'],
            'date': assessment_data['date'],
            'score': assessment_data['score'],
            'created_at': datetime.utcnow().isoformat()
        }
        assessment_arangodb_id = network_assessments.insert(assessment_doc)['_id']
        
        # Create relationships
        student_docs = list(network_students.find({'student_id': assessment_data['student_id']}))
        instructor_docs = list(network_instructors.find({'instructor_id': assessment_data['instructor_id']}))
        course_docs = list(network_courses.find({'course_id': assessment_data['course_id']}))
        
        if student_docs:
            student_arangodb_id = student_docs[0]['_id']
            # Student is assessed by the assessment
            network_assessed_by.insert({
                '_from': student_arangodb_id,
                '_to': assessment_arangodb_id,
                'created_at': datetime.utcnow().isoformat()
            })
        
        if instructor_docs:
            instructor_arangodb_id = instructor_docs[0]['_id']
            # Instructor created the assessment
            network_assessed_by.insert({
                '_from': assessment_arangodb_id,
                '_to': instructor_arangodb_id,
                'created_at': datetime.utcnow().isoformat()
            })
        
        if course_docs:
            course_arangodb_id = course_docs[0]['_id']
            # Assessment is part of the course
            network_part_of.insert({
                '_from': assessment_arangodb_id,
                '_to': course_arangodb_id,
                'created_at': datetime.utcnow().isoformat()
            })
    
    return {
        'students': network_students.count(),
        'instructors': network_instructors.count(),
        'courses': network_courses.count(),
        'assessments': network_assessments.count(),
        'teaches_edges': network_teaches.count(),
        'enrolled_in_edges': network_enrolled_in.count(),
        'assessed_by_edges': network_assessed_by.count(),
        'part_of_edges': network_part_of.count()
    }
```

## 4. ArangoDB Network Analysis

Create a new file `network_simulation/arango_network_analysis.py`:

```python
from users.arangodb import db

def get_student_instructor_network_aql():
    """
    Query ArangoDB to get student-instructor network data using AQL.
    Returns data formatted for visualization.
    """
    # AQL query to get all connections between students and instructors
    query = """
    FOR student IN network_students
        FOR assessed IN network_assessed_by
            FILTER assessed._from == student._id
            FOR assessment IN network_assessments
                FILTER assessed._to == assessment._id
                FOR assessed_by IN network_assessed_by
                    FILTER assessed_by._from == assessment._id
                    FOR instructor IN network_instructors
                        FILTER assessed_by._to == instructor._id
                        
                        COLLECT 
                            student_id = student.student_id, 
                            student_name = student.name,
                            instructor_id = instructor.instructor_id,
                            instructor_name = instructor.name
                        
                        AGGREGATE 
                            assessment_count = COUNT(),
                            avg_score = AVERAGE(assessment.score)
                        
                        RETURN {
                            "from": { 
                                "id": student_id, 
                                "name": student_name, 
                                "type": "student" 
                            },
                            "to": { 
                                "id": instructor_id, 
                                "name": instructor_name, 
                                "type": "instructor" 
                            },
                            "weight": assessment_count,
                            "avg_score": avg_score
                        }
    """
    results = list(db.aql.execute(query))
    
    # Format for visualization
    nodes = []
    edges = []
    node_map = {}  # To avoid duplicates
    
    for connection in results:
        # Add student node if not already added
        if connection['from']['id'] not in node_map:
            node_map[connection['from']['id']] = len(nodes)
            nodes.append({
                'id': connection['from']['id'],
                'name': connection['from']['name'],
                'type': 'student'
            })
        
        # Add instructor node if not already added
        if connection['to']['id'] not in node_map:
            node_map[connection['to']['id']] = len(nodes)
            nodes.append({
                'id': connection['to']['id'],
                'name': connection['to']['name'],
                'type': 'instructor'
            })
        
        # Add the edge
        edges.append({
            'source': node_map[connection['from']['id']],
            'target': node_map[connection['to']['id']],
            'weight': connection['weight'],
            'score': connection['avg_score']
        })
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def get_course_network_aql():
    """
    Query ArangoDB to get course network data using AQL.
    Returns data formatted for visualization.
    """
    # AQL query to find courses that share students
    query = """
    FOR course1 IN network_courses
        FOR e1 IN network_enrolled_in
            FILTER e1._to == course1._id
            FOR student IN network_students
                FILTER e1._from == student._id
                FOR e2 IN network_enrolled_in
                    FILTER e2._from == student._id AND e2._to != course1._id
                    FOR course2 IN network_courses
                        FILTER e2._to == course2._id
                        
                        COLLECT 
                            course1_id = course1.course_id, 
                            course1_name = course1.name,
                            course2_id = course2.course_id,
                            course2_name = course2.name
                        
                        AGGREGATE 
                            shared_students = COUNT()
                        
                        FILTER shared_students > 0
                        SORT shared_students DESC
                        
                        RETURN {
                            "from": { 
                                "id": course1_id, 
                                "name": course1_name, 
                                "type": "course" 
                            },
                            "to": { 
                                "id": course2_id, 
                                "name": course2_name, 
                                "type": "course" 
                            },
                            "shared_students": shared_students
                        }
    """
    results = list(db.aql.execute(query))
    
    # Format for visualization
    nodes = []
    edges = []
    node_map = {}  # To avoid duplicates
    
    for connection in results:
        # Add course1 node if not already added
        if connection['from']['id'] not in node_map:
            node_map[connection['from']['id']] = len(nodes)
            nodes.append({
                'id': connection['from']['id'],
                'name': connection['from']['name'],
                'type': 'course'
            })
        
        # Add course2 node if not already added
        if connection['to']['id'] not in node_map:
            node_map[connection['to']['id']] = len(nodes)
            nodes.append({
                'id': connection['to']['id'],
                'name': connection['to']['name'],
                'type': 'course'
            })
        
        # Add the edge (only if not duplicate)
        # We need to handle bidirectional connections
        sorted_pair = sorted([connection['from']['id'], connection['to']['id']])
        edge_key = f"{sorted_pair[0]}-{sorted_pair[1]}"
        
        # Simple way to check for duplicates
        duplicate = False
        for e in edges:
            if (e['source'] == node_map[connection['from']['id']] and 
                e['target'] == node_map[connection['to']['id']]) or \
               (e['source'] == node_map[connection['to']['id']] and 
                e['target'] == node_map[connection['from']['id']]):
                duplicate = True
                break
        
        if not duplicate:
            edges.append({
                'source': node_map[connection['from']['id']],
                'target': node_map[connection['to']['id']],
                'weight': connection['shared_students']
            })
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def get_student_performance_aql():
    """
    Query ArangoDB to get student performance analytics using AQL.
    """
    # Query to get GPA statistics
    gpa_query = """
    FOR student IN network_students
        COLLECT AGGREGATE 
            min_gpa = MIN(student.gpa),
            max_gpa = MAX(student.gpa),
            avg_gpa = AVERAGE(student.gpa)
        RETURN {
            "min": min_gpa,
            "max": max_gpa,
            "mean": avg_gpa
        }
    """
    gpa_stats = list(db.aql.execute(gpa_query))[0]
    
    # Query to get grade distribution by course
    grade_query = """
    FOR course IN network_courses
        LET enrollments = (
            FOR e IN network_enrolled_in
                FILTER e._to == course._id
                FILTER e.final_grade != null
                RETURN e.final_grade
        )
        
        FILTER LENGTH(enrollments) > 0
        
        LET min_grade = MIN(enrollments)
        LET max_grade = MAX(enrollments)
        LET avg_grade = AVERAGE(enrollments)
        LET count = LENGTH(enrollments)
        
        LET grade_a = LENGTH(FOR g IN enrollments FILTER g >= 90 RETURN g)
        LET grade_b = LENGTH(FOR g IN enrollments FILTER g >= 80 AND g < 90 RETURN g)
        LET grade_c = LENGTH(FOR g IN enrollments FILTER g >= 70 AND g < 80 RETURN g)
        LET grade_d = LENGTH(FOR g IN enrollments FILTER g >= 60 AND g < 70 RETURN g)
        LET grade_f = LENGTH(FOR g IN enrollments FILTER g < 60 RETURN g)
        
        RETURN {
            "course_id": course.course_id,
            "course_name": course.name,
            "stats": {
                "min": min_grade,
                "max": max_grade,
                "mean": avg_grade,
                "count": count,
                "distribution": {
                    "A": grade_a,
                    "B": grade_b,
                    "C": grade_c,
                    "D": grade_d,
                    "F": grade_f
                }
            }
        }
    """
    course_grades = list(db.aql.execute(grade_query))
    
    # Query to get top performing students
    top_students_query = """
    FOR student IN network_students
        SORT student.gpa DESC
        LIMIT 10
        RETURN {
            "id": student.student_id,
            "name": student.name,
            "gpa": student.gpa,
            "year": student.year
        }
    """
    top_students = list(db.aql.execute(top_students_query))
    
    # Query to get assessment performance by type
    assessment_query = """
    FOR assessment IN network_assessments
        COLLECT type = assessment.type
        AGGREGATE 
            min_score = MIN(assessment.score),
            max_score = MAX(assessment.score),
            avg_score = AVERAGE(assessment.score),
            count = COUNT()
        RETURN {
            "type": type,
            "stats": {
                "min": min_score,
                "max": max_score,
                "mean": avg_score,
                "count": count
            }
        }
    """
    assessment_types = list(db.aql.execute(assessment_query))
    
    return {
        "gpa_stats": gpa_stats,
        "course_grade_stats": {course["course_name"]: course["stats"] for course in course_grades},
        "top_students": top_students,
        "assessment_type_stats": {a["type"]: a["stats"] for a in assessment_types}
    }
```

## 5. Integration into Django Views

Update `network_simulation/views.py` to use the ArangoDB queries:

```python
from .arango_network_analysis import (
    get_student_instructor_network_aql,
    get_course_network_aql,
    get_student_performance_aql
)

def dashboard(request):
    """Network simulation dashboard view using ArangoDB data."""
    # Get network data from ArangoDB
    student_instructor_network = get_student_instructor_network_aql()
    course_network = get_course_network_aql()
    performance_analytics = get_student_performance_aql()
    
    # Prepare the context
    context = {
        'student_instructor_network': student_instructor_network,
        'course_network': course_network,
        'performance_analytics': performance_analytics,
        'use_arango': True  # Flag to indicate we're using ArangoDB data
    }
    
    return render(request, 'network_simulation/dashboard.html', context)
```

## 6. Command to Run Integration

Create a management command file `network_simulation/management/commands/import_network_to_arango.py`:

```python
from django.core.management.base import BaseCommand
from network_simulation.import_to_arango import import_network_to_arango

class Command(BaseCommand):
    help = 'Import network simulation data to ArangoDB'

    def add_arguments(self, parser):
        parser.add_argument('--json', type=str, default='network_data.json',
                            help='Path to network data JSON file')
        parser.add_argument('--csv-dir', type=str, default='csv_data',
                            help='Directory containing credential CSV files')

    def handle(self, *args, **options):
        json_file = options['json']
        csv_dir = options['csv_dir']
        
        self.stdout.write(self.style.SUCCESS(f'Importing network data from {json_file} to ArangoDB...'))
        result = import_network_to_arango(json_file, csv_dir)
        
        self.stdout.write(self.style.SUCCESS('Import completed!'))
        for entity, count in result.items():
            self.stdout.write(f'  - {entity}: {count}')
```

## 7. Usage Instructions

After implementing the above code:

1. Generate the network data with famous names:
   ```
   python manage.py runscript generate_data
   ```

2. Import the data to Django models:
   ```
   python manage.py runscript import_data
   ```

3. Import the network data to ArangoDB:
   ```
   python manage.py import_network_to_arango
   ```

4. Access the network visualization and analysis in the Django app:
   ```
   python manage.py runserver
   ```

5. Navigate to the network dashboard at `/network/` to see the visualizations and analysis using ArangoDB data.

## 8. Benefits of ArangoDB Integration

1. **Native Graph Operations**: Take advantage of ArangoDB's graph traversal algorithms
2. **Fast Graph Queries**: AQL allows for optimized graph queries
3. **Unified Data Model**: All entities and relationships in one database
4. **Scalability**: ArangoDB is designed to handle large-scale graph data
5. **Advanced Analytics**: Utilize graph analytics for educational insights