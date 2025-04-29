import csv
from django.core.management.base import BaseCommand
from users.arangodb import db

class Command(BaseCommand):
    help = 'Export user credentials to separate CSV files for instructors and students'

    def add_arguments(self, parser):
        parser.add_argument('--student-file', default='student_credentials.csv', help='Student CSV file path')
        parser.add_argument('--instructor-file', default='instructor_credentials.csv', help='Instructor CSV file path')

    def handle(self, *args, **options):
        student_file = options['student_file']
        instructor_file = options['instructor_file']
        
        self.stdout.write("Exporting user credentials to separate files...")
        
        try:
            # Query to get all users with their role, email, and ID
            query = """
            FOR user IN users
                SORT user.username
                RETURN {
                    id: user._id,
                    username: user.username,
                    email: user.email,
                    role: user.role,
                    raw_id: user.student_id || user.instructor_id || SPLIT(user._id, "/")[1]
                }
            """
            
            users = list(db.aql.execute(query))
            
            if not users:
                self.stderr.write("No users found in the database.")
                return
            
            # Separate users by role
            students = [user for user in users if user['role'] == 'student']
            instructors = [user for user in users if user['role'] == 'instructor']
            
            # Write students to CSV
            with open(student_file, 'w', newline='') as csvfile:
                fieldnames = ['username', 'email', 'password']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for user in students:
                    raw_id = user.get('raw_id', '').strip()
                    if not raw_id:
                        raw_id = user['id'].split('/')[1]
                    
                    password = f"pass_{raw_id}"
                    
                    writer.writerow({
                        'username': user['username'],
                        'email': user['email'],
                        'password': password
                    })
            
            # Write instructors to CSV
            with open(instructor_file, 'w', newline='') as csvfile:
                fieldnames = ['username', 'email', 'password']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for user in instructors:
                    raw_id = user.get('raw_id', '').strip()
                    if not raw_id:
                        raw_id = user['id'].split('/')[1]
                    
                    password = f"pass_{raw_id}"
                    
                    writer.writerow({
                        'username': user['username'],
                        'email': user['email'],
                        'password': password
                    })
            
            self.stdout.write(self.style.SUCCESS(f"Successfully exported {len(students)} student credentials to {student_file}"))
            self.stdout.write(self.style.SUCCESS(f"Successfully exported {len(instructors)} instructor credentials to {instructor_file}"))
        
        except Exception as e:
            self.stderr.write(f"Error exporting credentials: {e}")