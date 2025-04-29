import os
import django
import base64
import random
import json
import csv
from datetime import datetime, timedelta
import numpy as np
from faker import Faker

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import required modules
from users.arangodb import db

# Initialize Faker
fake = Faker()

# Create csv_data directory if it doesn't exist
os.makedirs('/app/csv_data', exist_ok=True)

# Function to generate fake PDF content (just a string representation)
def generate_fake_pdf_content(course_code, content_type):
    if content_type == "course_material":
        content = f"""
# 1 Introduction to {course_code}

This course introduces the fundamental concepts of {course_code} and explores
advanced topics in the field.

## 1.1 Course Overview

The course will cover theoretical foundations and practical applications.

# 2 Methodology

## 2.1 Theoretical Frameworks

We will examine various theoretical frameworks including:
- Framework A
- Framework B
- Framework C

## 2.2 Practical Application

Students will apply these frameworks to real-world problems.

# 3 Conclusion

By the end of this course, students should be able to:
1. Understand key concepts
2. Apply theoretical frameworks
3. Solve complex problems
"""
    elif content_type == "rubric":
        content = f"""
Grading Rubric for {course_code}

Technical Understanding - Points: 25: Demonstrates comprehensive understanding of technical concepts
Analytical Thinking - Points: 25: Shows strong analytical skills in problem-solving
Communication - Points: 20: Clearly articulates ideas and explanations
Creativity - Points: 15: Demonstrates innovative approaches to problems
Application - Points: 15: Successfully applies concepts to real-world scenarios
"""
    elif content_type == "solution":
        content = f"""
Q1: Explain the concept of backpropagation.
Answer: Backpropagation is an algorithm used in machine learning to train neural networks. It calculates the gradient of the loss function with respect to the weights of the network for a single input-output example, which is then used by an optimization algorithm to adjust the weights in order to minimize the loss function.

Q2: Describe the importance of data normalization.
Answer: Data normalization is important because it brings all features to a similar scale, preventing features with larger ranges from dominating the learning process. It helps models converge faster, improves numerical stability, and generally leads to better model performance and more accurate predictions.

Q3: What is the difference between supervised and unsupervised learning?
Answer: Supervised learning involves training a model on labeled data, where the algorithm learns to map inputs to known outputs. Unsupervised learning involves training a model on unlabeled data, where the algorithm learns to identify patterns or structures in the data without explicit guidance.
"""
    elif content_type == "instructions":
        content = f"""
Assignment Instructions for {course_code}

Q1: Explain the concept of backpropagation.

Q2: Describe the importance of data normalization.

Q3: What is the difference between supervised and unsupervised learning?
"""
    elif content_type == "student_submission":
        # Generate slightly different answers for each student
        quality = random.choice(["excellent", "good", "average", "poor"])
        
        if quality == "excellent":
            answer1 = "Backpropagation is a supervised learning algorithm for training artificial neural networks. It efficiently calculates the gradient of the loss function with respect to the network weights by utilizing the chain rule of calculus. This enables the weights to be updated through gradient descent to minimize the error."
            answer2 = "Data normalization is crucial in machine learning as it standardizes input features to have similar scales. This prevents features with larger magnitudes from dominating the learning process, leading to faster convergence, improved numerical stability, and better model performance overall."
            answer3 = "Supervised learning uses labeled data where the model learns to map inputs to known outputs, making predictions based on examples. Unsupervised learning works with unlabeled data, finding patterns and structures autonomously without explicit guidance. The key difference is that supervised learning has predefined correct answers while unsupervised learning discovers hidden patterns independently."
        elif quality == "good":
            answer1 = "Backpropagation is an algorithm used to train neural networks by calculating gradients. It works by propagating errors backwards through the network layers, updating weights to minimize the loss function."
            answer2 = "Data normalization is important because it brings features to a common scale. This helps prevent features with larger values from dominating the model training process and improves model performance."
            answer3 = "Supervised learning uses labeled data with known outputs, while unsupervised learning works with unlabeled data. Supervised learning makes predictions based on examples, while unsupervised learning finds patterns without guidance."
        elif quality == "average":
            answer1 = "Backpropagation is a method to train neural networks. It calculates errors and updates the weights in the network."
            answer2 = "Data normalization makes all data have similar scales. It helps the model train better and faster."
            answer3 = "Supervised learning uses data with labels, while unsupervised learning uses data without labels. One has the correct answers, the other doesn't."
        else:  # poor
            answer1 = "Backpropagation is when the computer learns from mistakes."
            answer2 = "Data normalization makes the numbers smaller and easier to work with."
            answer3 = "Supervised learning is when someone supervises the learning, unsupervised is when nobody supervises it."
            
        content = f"""
Q1: Explain the concept of backpropagation.
Answer: {answer1}

Q2: Describe the importance of data normalization.
Answer: {answer2}

Q3: What is the difference between supervised and unsupervised learning?
Answer: {answer3}
"""
        
    return content.strip()

# Function to generate base64 encoded string (simulating PDF content)
def generate_base64_pdf(content):
    # In a real scenario, we would create a PDF file
    # Here we're just encoding the text as if it were PDF content
    return base64.b64encode(content.encode()).decode()

# Function to create fake instructors and save to CSV
def create_instructors(num_instructors=3):
    instructors = []
    
    # Create CSV file for instructors
    with open('/app/csv_data/instructors.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Email', 'Password', 'ID'])
        
        for i in range(num_instructors):
            name = fake.name()
            email = f"{name.lower().replace(' ', '.')}@university.edu"
            password = "password"  # Same password for all users for simplicity
            
            instructor_data = {
                "username": name,
                "email": email,
                "password_hash": "$2b$12$dsrSPntSWEQCYkQQeR6uWep0pIxZwkpgou4clr0b1v726N7SKhLTu",  # "password"
                "role": "instructor",
                "created_at": datetime.utcnow().isoformat()
            }
            
            instructor_id = db.collection('users').insert(instructor_data)["_id"]
            instructors.append({"id": instructor_id, "name": name})
            
            # Write to CSV
            writer.writerow([name, email, password, instructor_id])
    
    print(f"Created {len(instructors)} instructors and saved to CSV")
    return instructors

# Function to create fake students and save to CSV
def create_students(num_students=10):
    students = []
    
    # Create CSV file for students
    with open('/app/csv_data/students.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Email', 'Password', 'ID', 'Courses'])
        
        for i in range(num_students):
            name = fake.name()
            email = f"{name.lower().replace(' ', '.')}@university.edu"
            password = "password"  # Same password for all users for simplicity
            
            student_data = {
                "username": name,
                "email": email,
                "password_hash": "$2b$12$dsrSPntSWEQCYkQQeR6uWep0pIxZwkpgou4clr0b1v726N7SKhLTu",  # "password"
                "role": "student",
                "created_at": datetime.utcnow().isoformat(),
                "courses": []
            }
            
            student_id = db.collection('users').insert(student_data)["_id"]
            students.append({"id": student_id, "name": name})
            
            # Write to CSV (courses will be updated later)
            writer.writerow([name, email, password, student_id, ""])
    
    print(f"Created {len(students)} students and saved to CSV")
    return students

# Function to create fake courses and save to CSV
def create_courses(instructors, num_courses=5):
    courses = []
    subjects = ["Computer Science", "Data Science", "Machine Learning", "Artificial Intelligence", "Big Data", "Computer Vision"]
    levels = ["Intro to", "Advanced", "Applied", "Theoretical", "Practical"]
    
    # Create CSV file for courses
    with open('/app/csv_data/courses.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Code', 'Course Title', 'Instructor ID', 'Instructor Name'])
        
        for i in range(num_courses):
            instructor = random.choice(instructors)
            subject = random.choice(subjects)
            level = random.choice(levels)
            course_code = f"COMP{5000 + i}"
            course_title = f"{level} {subject}"
            
            course_data = {
                "class_code": course_code,
                "class_title": course_title,
                "instructor_id": instructor["id"],
                "assignments": [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            course_id = db.collection('courses').insert(course_data)["_id"]
            courses.append({
                "id": course_id, 
                "code": course_code, 
                "title": course_title, 
                "instructor_id": instructor["id"],
                "instructor_name": instructor["name"]
            })
            
            # Write to CSV
            writer.writerow([course_code, course_title, instructor["id"], instructor["name"]])
    
    print(f"Created {len(courses)} courses and saved to CSV")
    return courses

# Function to parse rubric content
def parse_rubric_items(rubric_content):
    rubric_items = []
    for line in rubric_content.strip().split('\n'):
        if ' - Points: ' in line:
            try:
                criteria, rest = line.split(' - Points: ')
                points_str, description = rest.split(': ')
                points = float(points_str)
                
                rubric_items.append({
                    "criteria": criteria.strip(),
                    "points": points,
                    "description": description.strip()
                })
            except Exception as e:
                print(f"Error parsing rubric line: {line}. Error: {e}")
    return rubric_items

# Function to create text chunks and fake embeddings
def create_chunks_and_embeddings(text, chunk_size=500, chunk_overlap=50):
    # Split text into chunks manually
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    # Create fake embeddings (just random vectors)
    chunk_data = []
    for chunk in chunks:
        # Create a fake 384-dimensional embedding (common for sentence transformers)
        fake_embedding = [random.uniform(-1, 1) for _ in range(384)]
        chunk_data.append({
            "text": chunk,
            "embedding": fake_embedding
        })
    
    return chunks, chunk_data

# Function to split text into sections
def split_into_sections(text):
    sections = []
    lines = text.split("\n")
    current_section = {'title': '', 'content': ''}
    
    for line in lines:
        if line.startswith("# ") or line.startswith("## "):
            # Save previous section if it exists
            if current_section['title']:
                sections.append(current_section)
                
            # Start new section
            current_section = {'title': line, 'content': ''}
        else:
            # Add to current section content
            if current_section['content']:
                current_section['content'] += "\n" + line
            else:
                current_section['content'] = line
    
    # Add the last section
    if current_section['title']:
        sections.append(current_section)
        
    return sections

# Function to extract questions from text
def extract_questions(text):
    questions = []
    current_q = ""
    q_number = 0
    
    lines = text.split("\n")
    for line in lines:
        if line.startswith("Q") and ":" in line:
            # Save previous question if exists
            if current_q:
                questions.append({
                    "id": f"Q{q_number}",
                    "text": current_q.split(":", 1)[1].strip(),
                    "expected_answer": ""
                })
            
            # Start new question
            current_q = line
            q_number += 1
    
    # Add the last question
    if current_q:
        questions.append({
            "id": f"Q{q_number}",
            "text": current_q.split(":", 1)[1].strip(),
            "expected_answer": ""
        })
    
    return questions

# Function to create fake assignments for courses
def create_assignments(courses):
    assignments = []
    
    # Create CSV file for assignments
    with open('/app/csv_data/assignments.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Code', 'Assignment ID', 'Assignment Name', 'Due Date', 'Total Points'])
        
        for course in courses:
            # Create 1-3 assignments per course
            num_assignments = random.randint(1, 3)
            
            for j in range(num_assignments):
                assignment_name = f"Assignment {j+1}"
                due_date = (datetime.utcnow() + timedelta(days=random.randint(7, 30))).isoformat()
                total_points = 100
                
                # Generate fake assignment data
                assignment_id = f"{course['code']}_{j}"
                
                # Create materials for assignment
                course_material_content = generate_fake_pdf_content(course['code'], "course_material")
                rubric_content = generate_fake_pdf_content(course['code'], "rubric")
                solution_content = generate_fake_pdf_content(course['code'], "solution")
                instructions_content = generate_fake_pdf_content(course['code'], "instructions")
                
                # Encode as base64 (simulating PDFs)
                instructions_encoded = generate_base64_pdf(instructions_content)
                
                # Parse rubric items
                rubric_items = parse_rubric_items(rubric_content)
                
                # Add assignment to course
                course_doc = db.collection('courses').get(course['id'])
                new_assignment = {
                    "id": assignment_id,
                    "name": assignment_name,
                    "file_name": f"{assignment_name}.pdf",
                    "file_content": instructions_encoded,
                    "description": f"Assignment {j+1} for {course['title']}",
                    "due_date": due_date,
                    "total_points": total_points,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                if "assignments" not in course_doc:
                    course_doc["assignments"] = []
                    
                course_doc["assignments"].append(new_assignment)
                db.collection('courses').update(course_doc)
                
                assignments.append({
                    "course_id": course['id'],
                    "course_code": course['code'],
                    "assignment_id": assignment_id,
                    "assignment_name": assignment_name,
                    "course_material_content": course_material_content,
                    "rubric_content": rubric_content,
                    "rubric_items": rubric_items,
                    "solution_content": solution_content,
                    "instructions_content": instructions_content
                })
                
                # Write to CSV
                writer.writerow([course['code'], assignment_id, assignment_name, due_date, total_points])
    
    print(f"Created {len(assignments)} assignments and saved to CSV")
    return assignments

# Function to process course materials
def process_course_materials(assignments):
    for assignment in assignments:
        course_code = assignment['course_code']
        assignment_id = assignment['assignment_id']
        
        # Process course material text
        material_text = assignment['course_material_content']
        material_encoded = generate_base64_pdf(material_text)
        
        # 1. Store course material
        material_doc = {
            "class_code": course_code,
            "assignment_id": assignment_id,
            "file_name": f"{assignment['assignment_name']}_material.pdf",
            "file_content": material_encoded,
            "extracted_text": material_text,
            "created_at": datetime.utcnow().isoformat()
        }
        material_id = db.collection('course_materials').insert(material_doc)["_id"]
        
        # 2. Extract questions
        questions = extract_questions(assignment['instructions_content'])
        if questions:
            question_doc = {
                "class_code": course_code,
                "assignment_id": assignment_id,
                "questions": questions,
                "created_at": datetime.utcnow().isoformat()
            }
            db.collection('material_questions').insert(question_doc)
        
        # 3. Create chunks and embeddings
        chunks, chunk_data = create_chunks_and_embeddings(material_text)
        
        # Store vector embeddings
        for i, chunk in enumerate(chunk_data):
            vector_doc = {
                "class_code": course_code,
                "assignment_id": assignment_id,
                "chunk_id": i,
                "text": chunk["text"],
                "embedding": chunk["embedding"],
                "created_at": datetime.utcnow().isoformat()
            }
            db.collection('material_vectors').insert(vector_doc)
        
        # 4. Store rubric
        if assignment['rubric_items']:
            rubric_doc = {
                "class_code": course_code,
                "assignment_id": assignment_id,
                "items": assignment['rubric_items'],
                "created_at": datetime.utcnow().isoformat()
            }
            rubric_id = db.collection('rubrics').insert(rubric_doc)["_id"]
        
        # 5. Store sections
        sections = split_into_sections(material_text)
        for section in sections:
            section_doc = {
                "assignment_id": assignment_id,
                "class_code": course_code,
                "title": section["title"],
                "content": section["content"],
                "created_at": datetime.utcnow().isoformat()
            }
            db.collection('sections').insert(section_doc)
        
        print(f"Processed materials for {course_code} - {assignment['assignment_name']}")
        print(f"  - Created {len(chunks)} chunks")
        print(f"  - Created {len(sections)} sections")
        print(f"  - Added {len(assignment['rubric_items'])} rubric items")

# Function to enroll students in courses and update CSV
def enroll_students_in_courses(students, courses):
    enrollments = []
    
    # Create CSV file for enrollments
    with open('/app/csv_data/enrollments.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Course Title'])
        
        # Each student enrolls in 1-3 random courses
        for student in students:
            num_courses = random.randint(1, min(3, len(courses)))
            enrolled_courses = random.sample(courses, num_courses)
            
            # Update student document with enrolled courses
            student_doc = db.collection('users').get(student['id'])
            student_doc['courses'] = [course['code'] for course in enrolled_courses]
            db.collection('users').update(student_doc)
            
            # Write courses to CSV
            for course in enrolled_courses:
                enrollments.append({
                    "student_id": student['id'],
                    "student_name": student['name'],
                    "course_id": course['id'],
                    "course_code": course['code'],
                    "course_title": course['title']
                })
                
                # Write to CSV
                writer.writerow([student['id'], student['name'], course['code'], course['title']])
    
    # Update students.csv with course enrollments
    students_with_courses = []
    for student in students:
        student_doc = db.collection('users').get(student['id'])
        students_with_courses.append({
            "id": student['id'],
            "name": student['name'],
            "courses": student_doc.get('courses', [])
        })
    
    with open('/app/csv_data/students.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Email', 'Password', 'ID', 'Courses'])
        
        for student in students_with_courses:
            email = f"{student['name'].lower().replace(' ', '.')}@university.edu"
            writer.writerow([
                student['name'],
                email,
                'password',
                student['id'],
                ','.join(student['courses'])
            ])
    
    print(f"Created {len(enrollments)} enrollments and updated CSV files")
    return enrollments

# Function to create student submissions with grading
def create_student_submissions(students, enrollments, assignments):
    submissions = []
    
    # Create CSV file for submissions
    with open('/app/csv_data/submissions.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Student ID', 'Student Name', 'Course Code', 'Assignment ID', 'Grade', 'Submission ID'])
        
        for enrollment in enrollments:
            # Find assignments for this course
            course_assignments = [a for a in assignments if a['course_code'] == enrollment['course_code']]
            
            for assignment in course_assignments:
                # Generate student submission content
                submission_content = generate_fake_pdf_content(enrollment['course_code'], "student_submission")
                submission_encoded = generate_base64_pdf(submission_content)
                
                # Create submission in database
                submission_data = {
                    "user_id": enrollment['student_id'],
                    "class_code": enrollment['course_code'],
                    "assignment_id": assignment['assignment_id'],
                    "file_name": f"{enrollment['student_name']}_submission.pdf",
                    "file_content": submission_encoded,
                    "submission_date": datetime.now().isoformat(),
                    "grade": None,
                    "feedback": None,
                    "graded": False,
                    "ai_score": None,
                    "ai_feedback": None
                }
                
                submission_meta = db.collection('submission').insert(submission_data)
                submission_id = submission_meta['_id'].split('/')[1]  # Get numeric ID
                
                # Generate fake grades and feedback
                grade = random.uniform(70, 100)
                
                # Different feedback based on grade
                if grade >= 90:
                    feedback = "Excellent work! Your answers demonstrate comprehensive understanding."
                elif grade >= 80:
                    feedback = "Good job! You've shown good understanding of the concepts."
                elif grade >= 70:
                    feedback = "Satisfactory work. Some areas could use improvement."
                else:
                    feedback = "Needs improvement. Please review the course materials."
                
                # Update submission with grade and feedback
                submission_doc = db.collection('submission').get(submission_meta['_id'])
                submission_doc["ai_score"] = grade
                submission_doc["ai_feedback"] = [
                    {
                        "question": "Q1: Explain the concept of backpropagation.",
                        "score": random.uniform(grade-10, grade+10),
                        "justification": "Your explanation of backpropagation is " + ("thorough" if grade > 85 else "adequate" if grade > 75 else "lacking detail")
                    },
                    {
                        "question": "Q2: Describe the importance of data normalization.",
                        "score": random.uniform(grade-10, grade+10),
                        "justification": "Your discussion of data normalization is " + ("comprehensive" if grade > 85 else "generally accurate" if grade > 75 else "missing key points")
                    },
                    {
                        "question": "Q3: What is the difference between supervised and unsupervised learning?",
                        "score": random.uniform(grade-10, grade+10),
                        "justification": "Your comparison of supervised and unsupervised learning is " + ("clear and accurate" if grade > 85 else "somewhat clear" if grade > 75 else "unclear")
                    }
                ]
                db.collection('submission').update(submission_doc)
                
                # Create mistake nodes
                for feedback_item in submission_doc["ai_feedback"]:
                    question = feedback_item["question"]
                    score = feedback_item["score"]
                    justification = feedback_item["justification"]
                    
                    # Create mistake node only if score is less than perfect
                    if score < 90:
                        # Pick a random subset of rubric criteria that this mistake affects
                        rubric_criteria = random.sample([
                            "Technical Understanding", 
                            "Analytical Thinking", 
                            "Communication", 
                            "Creativity", 
                            "Application"
                        ], random.randint(1, 3))
                        
                        # Create mistake node
                        mistake_doc = {
                            "assignment_id": assignment['assignment_id'],
                            "question": question,
                            "justification": justification,
                            "score_awarded": score,
                            "rubric_criteria_names": rubric_criteria,
                            "created_at": datetime.utcnow().isoformat()
                        }
                        mistake_meta = db.collection('mistakes').insert(mistake_doc)
                        mistake_id = mistake_meta["_id"]
                        
                        # Create edges between nodes
                        try:
                            # Edge: Submission --> Mistake (has_feedback_on)
                            db.collection('has_feedback_on').insert({
                                "_from": f"submission/{submission_id}",
                                "_to": mistake_id
                            })
                            
                            # Find rubric doc for this assignment
                            rubric_docs = list(db.collection('rubrics').find({"assignment_id": assignment['assignment_id']}))
                            if rubric_docs:
                                rubric_id = rubric_docs[0]["_id"]
                                
                                # Edge: Mistake --> Rubric (affects_criteria)
                                db.collection('affects_criteria').insert({
                                    "_from": mistake_id,
                                    "_to": rubric_id
                                })
                            
                            # Find a random section to relate to this mistake
                            sections = list(db.collection('sections').find({"assignment_id": assignment['assignment_id']}))
                            if sections:
                                random_section = random.choice(sections)
                                section_id = random_section["_id"]
                                
                                # Edge: Mistake --> Section (related_to)
                                db.collection('related_to').insert({
                                    "_from": mistake_id,
                                    "_to": section_id
                                })
                        except Exception as e:
                            print(f"Error creating edges for mistake: {e}")
                
                submissions.append({
                    "submission_id": submission_meta['_id'],
                    "student_id": enrollment['student_id'],
                    "student_name": enrollment['student_name'],
                    "course_code": enrollment['course_code'],
                    "assignment_id": assignment['assignment_id'],
                    "grade": grade
                })
                
                # Write to CSV
                writer.writerow([
                    enrollment['student_id'],
                    enrollment['student_name'],
                    enrollment['course_code'],
                    assignment['assignment_id'],
                    f"{grade:.2f}",
                    submission_meta['_id']
                ])
                
                print(f"Created submission for {enrollment['student_name']} - {assignment['assignment_id']}")
    
    print(f"Created {len(submissions)} submissions and saved to CSV")
    return submissions

# Function to register the graph in ArangoDB
def register_graph():
    print("Registering educational network graph...")
    
    try:
        # Check if graph already exists
        if db.has_graph("educational_network"):
            print("  Graph already exists. Removing it first...")
            db.delete_graph("educational_network", drop_collections=False)
        
        # Create the graph with edge definitions
        graph = db.create_graph("educational_network")
        
        # Add edge definitions
        graph.create_edge_definition(
            edge_collection="has_feedback_on",
            from_vertex_collections=["submission"],
            to_vertex_collections=["mistakes"]
        )
        
        graph.create_edge_definition(
            edge_collection="affects_criteria",
            from_vertex_collections=["mistakes"],
            to_vertex_collections=["rubrics"]
        )
        
        graph.create_edge_definition(
            edge_collection="related_to",
            from_vertex_collections=["mistakes"],
            to_vertex_collections=["sections"]
        )
        
        # Add made_mistake edge collection
        graph.create_edge_definition(
            edge_collection="made_mistake",
            from_vertex_collections=["users"],
            to_vertex_collections=["mistakes"]
        )
        
        print("  Graph registered successfully")
    except Exception as e:
        print(f"  Error registering graph: {e}")

# Function to add student-to-mistake edges
def add_user_mistake_edges():
    print("Adding student-to-mistake edges...")
    
    query = """
    FOR s IN submission
        FOR edge IN has_feedback_on
            FILTER edge._from == s._id
            RETURN {
                user_id: s.user_id,
                mistake_id: edge._to
            }
    """
    
    pairs = list(db.aql.execute(query))
    added = 0
    
    for pair in pairs:
        try:
            db.collection('made_mistake').insert({
                "_from": f"users/{pair['user_id']}",
                "_to": pair['mistake_id']
            })
            added += 1
        except Exception as e:
            print(f"Error adding edge: {e}")
    
    print(f"Added {added} student-to-mistake edges")

# Main function to generate all data
def generate_all_data():
    print("Generating network data...")
    
    # Create users
    print("\nCreating instructors...")
    instructors = create_instructors(3)
    
    print("\nCreating students...")
    students = create_students(10)
    
    # Create courses
    print("\nCreating courses...")
    courses = create_courses(instructors, 5)
    
    # Create assignments
    print("\nCreating assignments...")
    assignments = create_assignments(courses)
    
    # Process course materials (simulating instructor uploads)
    print("\nProcessing course materials...")
    process_course_materials(assignments)
    
    # Enroll students in courses
    print("\nEnrolling students in courses...")
    enrollments = enroll_students_in_courses(students, courses)
    
    # Create student submissions
    print("\nCreating student submissions...")
    submissions = create_student_submissions(students, enrollments, assignments)
    
    # Register the graph
    print("\nRegistering the educational network graph...")
    register_graph()
    
    # Add user-mistake edges
    print("\nAdding user-mistake edges...")
    add_user_mistake_edges()
    
    print("\nNetwork data generation complete!")
    print("Login credentials have been saved to CSV files in the csv_data directory")

if __name__ == "__main__":
    generate_all_data()