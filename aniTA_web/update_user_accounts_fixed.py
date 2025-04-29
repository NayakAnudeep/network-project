#!/usr/bin/env python
import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from users.arangodb import db

def update_user_accounts():
    # Read instructor credentials
    instructor_data = []
    with open('/app/csv_data/instructor_credentials.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            instructor_data.append(row)
    
    # Read student credentials
    student_data = []
    with open('/app/csv_data/student_credentials.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            student_data.append(row)
    
    # Update user collection passwords in ArangoDB
    user_collection = db.collection('users')
    
    # Get all users
    all_users = list(user_collection.find({}))
    user_by_email = {user['email']: user for user in all_users if 'email' in user}
    
    # Update instructors
    updated_instructors = 0
    for instructor in instructor_data:
        if instructor['email'] in user_by_email:
            user_doc = user_by_email[instructor['email']]
            user_doc['password'] = instructor['password']
            user_collection.update(user_doc)
            updated_instructors += 1
            print(f"Updated instructor password for {instructor['email']}")
    
    # Update students
    updated_students = 0
    for student in student_data:
        if student['email'] in user_by_email:
            user_doc = user_by_email[student['email']]
            user_doc['password'] = student['password']
            user_collection.update(user_doc)
            updated_students += 1
            print(f"Updated student password for {student['email']}")
    
    print(f"Updated {updated_instructors} instructor accounts and {updated_students} student accounts in ArangoDB")
    
    # Copy credentials to /home/anudeepn/network-project/aniTA_web/csv_data/ directory
    os.system('mkdir -p /app/csv_data/exported/')
    os.system('cp /app/csv_data/instructor_credentials.csv /app/csv_data/exported/')
    os.system('cp /app/csv_data/student_credentials.csv /app/csv_data/exported/')
    print("Credentials exported to /app/csv_data/exported/ directory")

if __name__ == "__main__":
    update_user_accounts()