import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import the database
from users.arangodb import db

def get_users():
    print("INSTRUCTORS:")
    instructors = list(db.collection('users').find({"role": "instructor"}, limit=2))
    for i in instructors:
        print(f"Username: {i['username']}")
        print(f"Email: {i['email']}")
        print(f"ID: {i['_id']}")
        print()
    
    print("\nSTUDENTS:")
    students = list(db.collection('users').find({"role": "student"}, limit=2))
    for s in students:
        print(f"Username: {s['username']}")
        print(f"Email: {s['email']}")
        print(f"ID: {s['_id']}")
        print(f"Courses: {s.get('courses', [])}")
        print()
    
    print("\nPassword for all users: password")

if __name__ == "__main__":
    get_users()