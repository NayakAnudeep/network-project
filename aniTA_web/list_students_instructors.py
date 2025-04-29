#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from network_simulation.models import Instructor, Student

def list_students_and_instructors():
    # List instructors
    instructors = Instructor.objects.all()[:5]
    print(f"Sample Instructors (first 5 of {Instructor.objects.count()}):")
    for instructor in instructors:
        print(f" - {instructor}")
    
    # List students
    students = Student.objects.all()[:5]
    print(f"\nSample Students (first 5 of {Student.objects.count()}):")
    for student in students:
        print(f" - {student}")

if __name__ == "__main__":
    list_students_and_instructors()