import os
import django
import csv

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import the database
from users.arangodb import db

def update_csv_credentials():
    print("Updating CSV credential files...")
    
    # Update instructors.csv
    instructors = list(db.collection('users').find({"role": "instructor"}))
    with open('/app/csv_data/instructors.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Email', 'Password', 'ID'])
        
        for instructor in instructors:
            writer.writerow([
                instructor['username'],
                instructor['email'],
                'password',  # Password is now "password" for everyone
                instructor['_id']
            ])
    
    print(f"Updated {len(instructors)} instructors in CSV")
    
    # Update students.csv
    students = list(db.collection('users').find({"role": "student"}))
    with open('/app/csv_data/students.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Username', 'Email', 'Password', 'ID', 'Courses'])
        
        for student in students:
            writer.writerow([
                student['username'],
                student['email'],
                'password',  # Password is now "password" for everyone
                student['_id'],
                ','.join(student.get('courses', []))
            ])
    
    print(f"Updated {len(students)} students in CSV")
    
    print("\nCredential Summary:")
    print("====================")
    print("All users have the same password: 'password'")
    
    print("\nSample Instructors:")
    for i, instructor in enumerate(instructors[:2]):
        print(f"{i+1}. {instructor['username']} ({instructor['email']})")
    
    print("\nSample Students:")
    for i, student in enumerate(students[:2]):
        print(f"{i+1}. {student['username']} ({student['email']})")
        print(f"   Courses: {', '.join(student.get('courses', []))}")

if __name__ == "__main__":
    update_csv_credentials()