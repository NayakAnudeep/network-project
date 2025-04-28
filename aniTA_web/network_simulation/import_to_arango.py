"""
Import network simulation data to ArangoDB.

This module imports the generated network data into ArangoDB collections
to enable graph-based analytics and visualizations.
"""

import os
import json
import csv
from datetime import datetime
from users.arangodb import db, register_user

def import_network_to_arango(json_file, csv_dir=None):
    """
    Import network data from JSON and user credentials from CSV to ArangoDB.
    
    Parameters:
    - json_file: Path to the network data JSON file
    - csv_dir: Optional directory containing credential CSV files
    
    Returns:
        Dictionary with count of imported entities or error message
    """
    try:
        # Load network data
        with open(json_file, 'r') as f:
            network_data = json.load(f)
        
        # Load credentials if provided
        student_credentials = {}
        instructor_credentials = {}
        
        if csv_dir and os.path.exists(csv_dir):
            student_cred_path = os.path.join(csv_dir, 'student_credentials.csv')
            instructor_cred_path = os.path.join(csv_dir, 'instructor_credentials.csv')
            
            if os.path.exists(student_cred_path):
                with open(student_cred_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        student_credentials[row['id']] = row
            
            if os.path.exists(instructor_cred_path):
                with open(instructor_cred_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        instructor_credentials[row['id']] = row
        
        # Import students
        students_collection = db.collection('users')  # Using existing users collection
        for student_data in network_data['students']:
            student_id = student_data['id']
            
            # Skip if already exists
            if list(students_collection.find({'student_id': student_id})):
                continue
            
            # Create default email if not in credentials
            email = f"{student_data['name'].replace(' ', '.').lower()}@student.edu"
            password = f"pass_{student_id}"
            
            if student_id in student_credentials:
                cred = student_credentials[student_id]
                email = cred.get('email', email)
                password = cred.get('password', password)
            
            # Register user in ArangoDB
            result = register_user(
                username=student_data['name'],
                email=email,
                password=password,
                role="student"
            )
            
            # If registered successfully, update with additional student data
            if 'success' in result:
                # Find the newly created user
                user = list(students_collection.find({'email': email}))[0]
                
                # Update with student-specific data
                user.update({
                    'student_id': student_id,
                    'year': student_data['year'],
                    'major': student_data['major'],
                    'gpa': student_data['gpa'],
                    'is_simulated': True  # Flag to identify simulated users
                })
                
                students_collection.update(user)
        
        # Import instructors
        instructors_collection = db.collection('users')  # Using existing users collection
        for instructor_data in network_data['instructors']:
            instructor_id = instructor_data['id']
            
            # Skip if already exists
            if list(instructors_collection.find({'instructor_id': instructor_id})):
                continue
            
            # Create default email if not in credentials
            email = f"{instructor_data['name'].replace(' ', '.').lower()}@faculty.edu"
            password = f"pass_{instructor_id}"
            
            if instructor_id in instructor_credentials:
                cred = instructor_credentials[instructor_id]
                email = cred.get('email', email)
                password = cred.get('password', password)
            
            # Register user in ArangoDB
            result = register_user(
                username=instructor_data['name'],
                email=email,
                password=password,
                role="instructor"
            )
            
            # If registered successfully, update with additional instructor data
            if 'success' in result:
                # Find the newly created user
                user = list(instructors_collection.find({'email': email}))[0]
                
                # Update with instructor-specific data
                user.update({
                    'instructor_id': instructor_id,
                    'department': instructor_data['department'],
                    'specialization': instructor_data['specialization'],
                    'is_simulated': True  # Flag to identify simulated users
                })
                
                instructors_collection.update(user)
        
        # Import courses
        courses_collection = db.collection('courses')
        for course_data in network_data['courses']:
            course_id = course_data['id']
            
            # Skip if already exists
            if list(courses_collection.find({'course_id': course_id})):
                continue
            
            # Get instructor users
            instructor_documents = []
            for instructor_id in course_data['instructor_ids']:
                instructor_docs = list(instructors_collection.find({'instructor_id': instructor_id}))
                if instructor_docs:
                    instructor_documents.append(instructor_docs[0])
            
            # Create course document with primary instructor
            primary_instructor_id = instructor_documents[0]['_id'] if instructor_documents else None
            
            course_doc = {
                'course_id': course_id,
                'class_code': course_id,  # Match existing schema
                'class_title': course_data['name'],
                'instructor_id': primary_instructor_id,
                'credits': course_data['credits'],
                'assignments': [],
                'created_at': datetime.utcnow().isoformat(),
                'is_simulated': True  # Flag to identify simulated courses
            }
            
            # Insert course
            courses_collection.insert(course_doc)
        
        # Process enrollments by adding courses to student user documents
        for enrollment_data in network_data['enrollments']:
            student_id = enrollment_data['student_id']
            course_id = enrollment_data['course_id']
            
            # Find student and course
            student_docs = list(students_collection.find({'student_id': student_id}))
            course_docs = list(courses_collection.find({'course_id': course_id}))
            
            if student_docs and course_docs:
                student = student_docs[0]
                
                # Add course to student's courses list if not already there
                if 'courses' not in student:
                    student['courses'] = []
                    
                if course_id not in student['courses']:
                    student['courses'].append(course_id)
                    students_collection.update(student)
        
        # Process assessments by creating assignments and submissions
        submission_collection = db.collection('submission')
        
        for assessment_data in network_data['assessments']:
            assessment_id = assessment_data['id']
            student_id = assessment_data['student_id']
            course_id = assessment_data['course_id']
            instructor_id = assessment_data['instructor_id']
            
            # Skip if already exists
            if list(submission_collection.find({'assessment_id': assessment_id})):
                continue
            
            # Find related documents
            student_docs = list(students_collection.find({'student_id': student_id}))
            course_docs = list(courses_collection.find({'course_id': course_id}))
            instructor_docs = list(instructors_collection.find({'instructor_id': instructor_id}))
            
            if student_docs and course_docs and instructor_docs:
                student = student_docs[0]
                course = course_docs[0]
                instructor = instructor_docs[0]
                
                # Ensure the course has an assignment for this assessment
                course_assignments = course.get('assignments', [])
                
                # Find or create an assignment based on the assessment type
                assignment_id = f"{course_id}_{assessment_data['type']}_{assessment_data['term']}"
                
                assignment_exists = False
                for assignment in course_assignments:
                    if assignment.get('id') == assignment_id:
                        assignment_exists = True
                        break
                
                if not assignment_exists:
                    # Create a new assignment
                    new_assignment = {
                        'id': assignment_id,
                        'name': f"{assessment_data['type']} {assessment_data['term']}",
                        'description': f"Simulated {assessment_data['type']} for term {assessment_data['term']}",
                        'due_date': assessment_data['date'],
                        'total_points': 100,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                    course_assignments.append(new_assignment)
                    course['assignments'] = course_assignments
                    courses_collection.update(course)
                
                # Create a submission for this assessment
                submission_data = {
                    'user_id': student['_id'],
                    'class_code': course_id,
                    'assignment_id': assignment_id,
                    'assessment_id': assessment_id,  # Link to original assessment
                    'file_name': f"simulated_submission_{assessment_id}.pdf",
                    'file_content': "Simulated submission content",
                    'submission_date': assessment_data['date'],
                    'grade': assessment_data['score'],
                    'feedback': f"Simulated feedback for {assessment_data['type']}",
                    'graded': True,
                    'is_simulated': True
                }
                
                submission_collection.insert(submission_data)
        
        # Set up graph relationship edges using made_mistake collection
        # This connects students to common mistakes based on assessment scores
        mistakes_collection = db.collection('mistakes')
        made_mistake_collection = db.collection('made_mistake')
        
        # Create some simulated mistake patterns based on lower scores
        mistake_patterns = [
            {"threshold": 60, "topic": "Fundamental Concepts", "justification": "Missing understanding of basic principles"},
            {"threshold": 70, "topic": "Application of Knowledge", "justification": "Cannot apply concepts to problems"},
            {"threshold": 80, "topic": "Analysis Skills", "justification": "Weak analytical reasoning"},
            {"threshold": 90, "topic": "Advanced Synthesis", "justification": "Incomplete synthesis of complex ideas"}
        ]
        
        # For each low-score assessment, create mistake edges
        for assessment_data in network_data['assessments']:
            if assessment_data['score'] < 90:  # Only process lower scores
                student_id = assessment_data['student_id']
                
                # Find student
                student_docs = list(students_collection.find({'student_id': student_id}))
                if not student_docs:
                    continue
                
                student = student_docs[0]
                student_arango_id = student['_id']
                
                # Determine mistake pattern based on score
                for pattern in mistake_patterns:
                    if assessment_data['score'] < pattern['threshold']:
                        # Create or find a mistake
                        mistake_query = f"""
                        FOR m IN mistakes
                            FILTER m.question == "{pattern['topic']}" AND 
                                m.justification == "{pattern['justification']}"
                            RETURN m
                        """
                        existing_mistakes = list(db.aql.execute(mistake_query))
                        
                        if existing_mistakes:
                            mistake = existing_mistakes[0]
                        else:
                            # Create new mistake
                            mistake_data = {
                                'question': pattern['topic'],
                                'justification': pattern['justification'],
                                'score_awarded': assessment_data['score'],
                                'rubric_criteria_names': [course_id, assessment_data['type']],
                                'is_simulated': True
                            }
                            mistake_id = mistakes_collection.insert(mistake_data)['_id']
                            mistake = mistakes_collection.get(mistake_id)
                        
                        # Connect student to mistake if not already connected
                        edge_query = f"""
                        FOR edge IN made_mistake
                            FILTER edge._from == "{student_arango_id}" AND 
                                edge._to == "{mistake['_id']}"
                            RETURN edge
                        """
                        existing_edges = list(db.aql.execute(edge_query))
                        
                        if not existing_edges:
                            made_mistake_collection.insert({
                                '_from': student_arango_id,
                                '_to': mistake['_id'],
                                'created_at': datetime.utcnow().isoformat(),
                                'is_simulated': True
                            })
        
        # Return statistics on imported entities
        return {
            'students': len(list(students_collection.find({'is_simulated': True}))),
            'instructors': len(list(instructors_collection.find({'is_simulated': True}))),
            'courses': len(list(courses_collection.find({'is_simulated': True}))),
            'submissions': len(list(submission_collection.find({'is_simulated': True}))),
            'mistakes': len(list(mistakes_collection.find({'is_simulated': True}))),
            'made_mistake_edges': len(list(db.aql.execute('FOR e IN made_mistake FILTER e.is_simulated == true RETURN e')))
        }
    
    except Exception as e:
        print(f"Error importing network data to ArangoDB: {e}")
        return {'error': str(e)}