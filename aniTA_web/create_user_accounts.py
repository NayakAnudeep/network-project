#!/usr/bin/env python
import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from django.contrib.auth.models import User
from network_simulation.models import Instructor, Student

def create_user_accounts():
    # Create instructor accounts
    instructor_data = []
    for instructor in Instructor.objects.all():
        username = f"instructor_{instructor.instructor_id}"
        email = f"{username}@example.com"
        password = "password"
        
        # Check if user already exists
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            print(f"Created instructor user: {username}")
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"Reset password for instructor: {username}")
            
        instructor_data.append([
            instructor.instructor_id,
            instructor.name,
            username,
            email,
            password
        ])
    
    # Create student accounts
    student_data = []
    for student in Student.objects.all():
        username = f"student_{student.student_id}"
        email = f"{username}@example.com"
        password = "password"
        
        # Check if user already exists
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            print(f"Created student user: {username}")
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"Reset password for student: {username}")
            
        student_data.append([
            student.student_id,
            student.name,
            username,
            email,
            password
        ])
    
    # Save to CSV files
    with open('/app/csv_data/instructor_accounts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Username', 'Email', 'Password'])
        writer.writerows(instructor_data)
    
    with open('/app/csv_data/student_accounts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Username', 'Email', 'Password'])
        writer.writerows(student_data)
    
    print(f"Created {len(instructor_data)} instructor accounts and {len(student_data)} student accounts")
    print("Account details saved to /app/csv_data/instructor_accounts.csv and /app/csv_data/student_accounts.csv")

if __name__ == "__main__":
    create_user_accounts()