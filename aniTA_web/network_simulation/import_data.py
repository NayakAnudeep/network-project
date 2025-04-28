import os
import json
import csv
import datetime
import django
from django.db import transaction

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import models
from network_simulation.models import Student, Instructor, Course, Enrollment, Assessment

def import_from_json(json_file):
    """Import data from the generated JSON file into Django models."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    with transaction.atomic():
        # Clear existing data
        Assessment.objects.all().delete()
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        
        # Import instructors
        instructors_map = {}
        for instructor_data in data['instructors']:
            instructor = Instructor.objects.create(
                instructor_id=instructor_data['id'],
                name=instructor_data['name'],
                department=instructor_data['department'],
                specialization=instructor_data['specialization']
            )
            instructors_map[instructor_data['id']] = instructor
        
        # Import courses
        courses_map = {}
        for course_data in data['courses']:
            course = Course.objects.create(
                course_id=course_data['id'],
                name=course_data['name'],
                credits=course_data['credits']
            )
            
            # Add instructors to course
            for instructor_id in course_data['instructor_ids']:
                if instructor_id in instructors_map:
                    course.instructors.add(instructors_map[instructor_id])
            
            courses_map[course_data['id']] = course
        
        # Import students
        students_map = {}
        for student_data in data['students']:
            student = Student.objects.create(
                student_id=student_data['id'],
                name=student_data['name'],
                year=student_data['year'],
                major=student_data['major'],
                gpa=student_data['gpa']
            )
            students_map[student_data['id']] = student
        
        # Import enrollments
        enrollments_map = {}
        for enrollment_data in data['enrollments']:
            student = students_map.get(enrollment_data['student_id'])
            course = courses_map.get(enrollment_data['course_id'])
            
            if student and course:
                enrollment = Enrollment.objects.create(
                    student=student,
                    course=course,
                    term=enrollment_data['term'],
                    year=enrollment_data['year'],
                    final_grade=enrollment_data['final_grade']
                )
                
                # Create a unique key for this enrollment
                enroll_key = (
                    enrollment_data['student_id'],
                    enrollment_data['course_id'],
                    enrollment_data['term'],
                    enrollment_data['year']
                )
                enrollments_map[enroll_key] = enrollment
        
        # Import assessments
        for assessment_data in data['assessments']:
            student = students_map.get(assessment_data['student_id'])
            course = courses_map.get(assessment_data['course_id'])
            instructor = instructors_map.get(assessment_data['instructor_id'])
            
            if student and course and instructor:
                Assessment.objects.create(
                    assessment_id=assessment_data['id'],
                    student=student,
                    course=course,
                    instructor=instructor,
                    term=assessment_data['term'],
                    year=assessment_data['year'],
                    type=assessment_data['type'],
                    date=datetime.date.fromisoformat(assessment_data['date']),
                    score=assessment_data['score']
                )

def import_from_csv(csv_dir):
    """Import data from the generated CSV files into Django models."""
    with transaction.atomic():
        # Clear existing data
        Assessment.objects.all().delete()
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        
        # Import instructors
        instructors_map = {}
        with open(os.path.join(csv_dir, 'instructors.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                instructor = Instructor.objects.create(
                    instructor_id=row['id'],
                    name=row['name'],
                    department=row['department'],
                    specialization=row['specialization']
                )
                instructors_map[row['id']] = instructor
        
        # Import courses
        courses_map = {}
        with open(os.path.join(csv_dir, 'courses.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course = Course.objects.create(
                    course_id=row['id'],
                    name=row['name'],
                    credits=int(row['credits'])
                )
                
                # Add instructors to course
                instructor_ids = row['instructor_ids'].split(',')
                for instructor_id in instructor_ids:
                    if instructor_id in instructors_map:
                        course.instructors.add(instructors_map[instructor_id])
                
                courses_map[row['id']] = course
        
        # Import students
        students_map = {}
        with open(os.path.join(csv_dir, 'students.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student.objects.create(
                    student_id=row['id'],
                    name=row['name'],
                    year=int(row['year']),
                    major=row['major'],
                    gpa=float(row['gpa'])
                )
                students_map[row['id']] = student
        
        # Import enrollments
        enrollments_map = {}
        with open(os.path.join(csv_dir, 'enrollments.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = students_map.get(row['student_id'])
                course = courses_map.get(row['course_id'])
                
                if student and course:
                    final_grade = float(row['final_grade']) if row['final_grade'] and row['final_grade'] != 'None' else None
                    
                    enrollment = Enrollment.objects.create(
                        student=student,
                        course=course,
                        term=int(row['term']),
                        year=int(row['year']),
                        final_grade=final_grade
                    )
                    
                    # Create a unique key for this enrollment
                    enroll_key = (
                        row['student_id'],
                        row['course_id'],
                        int(row['term']),
                        int(row['year'])
                    )
                    enrollments_map[enroll_key] = enrollment
        
        # Import assessments
        with open(os.path.join(csv_dir, 'assessments.csv'), 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = students_map.get(row['student_id'])
                course = courses_map.get(row['course_id'])
                instructor = instructors_map.get(row['instructor_id'])
                
                if student and course and instructor:
                    Assessment.objects.create(
                        assessment_id=row['id'],
                        student=student,
                        course=course,
                        instructor=instructor,
                        term=int(row['term']),
                        year=int(row['year']),
                        type=row['type'],
                        date=datetime.date.fromisoformat(row['date']),
                        score=float(row['score'])
                    )

if __name__ == "__main__":
    # First generate the data (ensure the generate_data.py script is run first)
    
    # Option 1: Import from JSON
    print("Importing data from JSON...")
    import_from_json('network_data.json')
    
    # Option 2: Import from CSV
    # print("Importing data from CSV...")
    # import_from_csv('csv_data')
    
    # Print statistics
    print("\nImport completed successfully!")
    print(f"Students: {Student.objects.count()}")
    print(f"Instructors: {Instructor.objects.count()}")
    print(f"Courses: {Course.objects.count()}")
    print(f"Enrollments: {Enrollment.objects.count()}")
    print(f"Assessments: {Assessment.objects.count()}")
