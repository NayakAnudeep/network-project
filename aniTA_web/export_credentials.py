#!/usr/bin/env python
import os
import django
import csv
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

def export_credentials():
    # Create export directory
    os.makedirs('/app/csv_data/exported', exist_ok=True)
    
    # Copy the credential files
    shutil.copy('/app/csv_data/instructor_credentials.csv', '/app/csv_data/exported/instructor_credentials.csv')
    shutil.copy('/app/csv_data/student_credentials.csv', '/app/csv_data/exported/student_credentials.csv')
    
    print("Exported credential files to /app/csv_data/exported/")
    
    # Print sample credentials for quick reference
    print("\nSample Instructor Credentials:")
    with open('/app/csv_data/instructor_credentials.csv', 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 3:
                print(f"ID: {row['id']}, Email: {row['email']}, Password: {row['password']}")
            else:
                break
    
    print("\nSample Student Credentials:")
    with open('/app/csv_data/student_credentials.csv', 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 3:
                print(f"ID: {row['id']}, Email: {row['email']}, Password: {row['password']}")
            else:
                break

if __name__ == "__main__":
    export_credentials()