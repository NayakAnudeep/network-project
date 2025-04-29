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
    
    # Update instructors
    for instructor in instructor_data:
        user_doc = user_collection.find_one({'email': instructor['email']})
        if user_doc:
            user_doc['password'] = instructor['password']
            user_collection.update(user_doc)
            print(f"Updated instructor password for {instructor['email']}")
    
    # Update students
    for student in student_data:
        user_doc = user_collection.find_one({'email': student['email']})
        if user_doc:
            user_doc['password'] = student['password']
            user_collection.update(user_doc)
            print(f"Updated student password for {student['email']}")
    
    print(f"Updated {len(instructor_data)} instructor accounts and {len(student_data)} student accounts in ArangoDB")

if __name__ == "__main__":
    update_user_accounts()