import random
import datetime
import csv
import os
import json

# Configuration
NUM_COURSES = 6
NUM_INSTRUCTORS = 12
NUM_STUDENTS = 180
STUDENTS_PER_COURSE = 35
TERMS = 2
ASSESSMENTS_PER_TERM = 3
ACADEMIC_YEAR = 2023  # Starting year

# Lists for names - Famous scientists, artists, inventors, and other notable figures
FIRST_NAMES = [
    "Albert", "Marie", "Nikola", "Ada", "Leonardo", "Frida", "Isaac", "Grace",
    "Stephen", "Maya", "Wolfgang", "Jane", "Richard", "Emmy", "Charles", "Rosalind",
    "Alan", "Katherine", "Neil", "Hedy", "Thomas", "Margaret", "Carl", "Rachel",
    "Louis", "Virginia", "Max", "Toni", "Galileo", "Florence", "Alexander", "Rosa",
    "Srinivasa", "Eleanor", "Ernest", "Barbara", "Johannes", "Georgia", "James", "Dorothy",
    "Niels", "Sylvia", "Werner", "Zora", "Enrico", "Mary", "Robert", "Elizabeth",
    "Mahatma", "Malala", "Nelson", "Amelia", "Winston", "Cleopatra", "Martin", "Marie",
    "Nikola", "Frida", "Steve", "Michelle", "Bill", "Ruth", "Elon", "Oprah"
]

LAST_NAMES = [
    "Einstein", "Curie", "Tesla", "Lovelace", "da Vinci", "Kahlo", "Newton", "Hopper",
    "Hawking", "Angelou", "Mozart", "Austen", "Feynman", "Noether", "Darwin", "Franklin",
    "Turing", "Johnson", "Armstrong", "Lamarr", "Edison", "Mead", "Sagan", "Carson",
    "Pasteur", "Woolf", "Planck", "Morrison", "Galilei", "Nightingale", "Graham", "Parks",
    "Ramanujan", "Roosevelt", "Hemingway", "McClintock", "Kepler", "O'Keeffe", "Watson", "Hodgkin",
    "Bohr", "Plath", "Heisenberg", "Hurston", "Fermi", "Shelley", "Oppenheimer", "Blackwell",
    "Gandhi", "Yousafzai", "Mandela", "Earhart", "Churchill", "Ptolemy", "Luther", "Antoinette",
    "Tesla", "Kahlo", "Jobs", "Obama", "Gates", "Ginsburg", "Musk", "Winfrey"
]

SUBJECTS = [
    "Introduction to Computer Science",
    "Data Structures and Algorithms",
    "Database Systems",
    "Computer Networks",
    "Machine Learning",
    "Software Engineering"
]

# Utility functions
def generate_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def generate_random_id(prefix, num_digits=5):
    return f"{prefix}{random.randint(10**(num_digits-1), 10**num_digits-1)}"

def generate_random_grade():
    # Generate grades with a normal distribution (mean=75, std_dev=10)
    grade = random.normalvariate(75, 10)
    return max(0, min(100, grade))  # Clamp between 0 and 100

# Data generation
def generate_data():
    data = {
        "students": [],
        "instructors": [],
        "courses": [],
        "enrollments": [],
        "assessments": []
    }
    
    # Generate instructors
    for i in range(NUM_INSTRUCTORS):
        instructor = {
            "id": generate_random_id("I", 3),
            "name": generate_random_name(),
            "department": "Computer Science",
            "specialization": random.choice([
                "Algorithms", "Networks", "Databases", "AI/ML", 
                "Software Engineering", "Theory of Computation"
            ])
        }
        data["instructors"].append(instructor)
    
    # Generate courses
    for i, subject in enumerate(SUBJECTS):
        # Assign 1-3 instructors per course
        course_instructors = random.sample(
            data["instructors"], 
            min(random.randint(1, 3), len(data["instructors"]))
        )
        
        course = {
            "id": f"CS{i+101}",
            "name": subject,
            "instructor_ids": [inst["id"] for inst in course_instructors],
            "credits": random.choice([3, 4])
        }
        data["courses"].append(course)
    
    # Generate students
    for i in range(NUM_STUDENTS):
        student = {
            "id": generate_random_id("S", 5),
            "name": generate_random_name(),
            "year": random.randint(1, 4),  # 1=freshman, 4=senior
            "major": "Computer Science",
            "gpa": round(random.uniform(2.0, 4.0), 2)
        }
        data["students"].append(student)
    
    # Generate enrollments and assessments
    assessment_id_counter = 1
    
    for term in range(1, TERMS + 1):
        term_start = datetime.date(ACADEMIC_YEAR, 1 if term == 1 else 8, 15)
        
        for course in data["courses"]:
            # Select students for this course
            course_students = random.sample(
                data["students"], 
                min(STUDENTS_PER_COURSE, len(data["students"]))
            )
            
            # Create enrollments
            for student in course_students:
                enrollment = {
                    "student_id": student["id"],
                    "course_id": course["id"],
                    "term": term,
                    "year": ACADEMIC_YEAR,
                    "final_grade": None  # Will be calculated from assessments
                }
                data["enrollments"].append(enrollment)
                
                # Generate assessments for this student in this course
                for assessment_num in range(1, ASSESSMENTS_PER_TERM + 1):
                    # Spread assessments throughout the term
                    assessment_date = term_start + datetime.timedelta(
                        days=int(30 * (assessment_num / (ASSESSMENTS_PER_TERM + 1)))
                    )
                    
                    # Choose a random instructor from those teaching the course
                    instructor_id = random.choice(course["instructor_ids"])
                    
                    assessment = {
                        "id": f"A{assessment_id_counter:06d}",
                        "student_id": student["id"],
                        "course_id": course["id"],
                        "instructor_id": instructor_id,
                        "term": term,
                        "year": ACADEMIC_YEAR,
                        "type": random.choice(["Quiz", "Exam", "Project", "Homework"]),
                        "date": assessment_date.isoformat(),
                        "score": generate_random_grade()
                    }
                    data["assessments"].append(assessment)
                    assessment_id_counter += 1
    
    # Calculate final grades based on assessments
    for enrollment in data["enrollments"]:
        # Get all assessments for this student in this course
        student_assessments = [
            a for a in data["assessments"] 
            if a["student_id"] == enrollment["student_id"] 
            and a["course_id"] == enrollment["course_id"]
            and a["term"] == enrollment["term"]
            and a["year"] == enrollment["year"]
        ]
        
        if student_assessments:
            # Calculate average score
            avg_score = sum(a["score"] for a in student_assessments) / len(student_assessments)
            enrollment["final_grade"] = round(avg_score, 1)
    
    return data

def save_data_as_csv(data, output_dir):
    """Save the generated data as CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save students
    with open(os.path.join(output_dir, 'students.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'year', 'major', 'gpa'])
        for student in data['students']:
            writer.writerow([
                student['id'], student['name'], student['year'], 
                student['major'], student['gpa']
            ])
    
    # Save instructors
    with open(os.path.join(output_dir, 'instructors.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'department', 'specialization'])
        for instructor in data['instructors']:
            writer.writerow([
                instructor['id'], instructor['name'], 
                instructor['department'], instructor['specialization']
            ])
    
    # Save courses
    with open(os.path.join(output_dir, 'courses.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'instructor_ids', 'credits'])
        for course in data['courses']:
            writer.writerow([
                course['id'], course['name'], 
                ','.join(course['instructor_ids']), course['credits']
            ])
    
    # Save enrollments
    with open(os.path.join(output_dir, 'enrollments.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['student_id', 'course_id', 'term', 'year', 'final_grade'])
        for enrollment in data['enrollments']:
            writer.writerow([
                enrollment['student_id'], enrollment['course_id'],
                enrollment['term'], enrollment['year'], enrollment['final_grade']
            ])
    
    # Save assessments
    with open(os.path.join(output_dir, 'assessments.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'student_id', 'course_id', 'instructor_id', 
            'term', 'year', 'type', 'date', 'score'
        ])
        for assessment in data['assessments']:
            writer.writerow([
                assessment['id'], assessment['student_id'], assessment['course_id'],
                assessment['instructor_id'], assessment['term'], assessment['year'],
                assessment['type'], assessment['date'], assessment['score']
            ])

def save_data_as_json(data, output_file):
    """Save the generated data as a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

def save_user_credentials_csv(data, output_dir):
    """Save user credentials as CSV files for simulated users."""
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

if __name__ == "__main__":
    # Generate the data
    print("Generating educational network data...")
    network_data = generate_data()
    
    # Save as CSV files
    output_dir = "csv_data"
    save_data_as_csv(network_data, output_dir)
    print(f"CSV data saved to {output_dir}/")
    
    # Save user credentials
    save_user_credentials_csv(network_data, output_dir)
    print(f"User credentials saved to {output_dir}/")
    
    # Save as JSON
    json_file = "network_data.json"
    save_data_as_json(network_data, json_file)
    print(f"JSON data saved to {json_file}")
    
    # Print some statistics
    print("\nData Statistics:")
    print(f"Number of students: {len(network_data['students'])}")
    print(f"Number of instructors: {len(network_data['instructors'])}")
    print(f"Number of courses: {len(network_data['courses'])}")
    print(f"Number of enrollments: {len(network_data['enrollments'])}")
    print(f"Number of assessments: {len(network_data['assessments'])}")
