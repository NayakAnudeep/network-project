"""
Mark all simulated submissions as graded in ArangoDB.

This script connects to ArangoDB and updates all simulated submissions 
to be marked as graded, ensuring they appear properly in the dashboard.
"""

from django.core.management.base import BaseCommand
from users.arangodb import db

class Command(BaseCommand):
    help = 'Mark all simulated submissions as graded in ArangoDB'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to mark simulated submissions as graded...'))
        
        try:
            # Query to mark all simulated submissions as graded
            mark_submissions_query = """
            FOR sub IN submission
                FILTER sub.is_simulated == true
                UPDATE sub WITH { graded: true } IN submission
                RETURN { modified: OLD._id }
            """
            
            # Execute the query
            result = list(db.aql.execute(mark_submissions_query))
            
            # Report results
            self.stdout.write(self.style.SUCCESS(f'Successfully marked {len(result)} submissions as graded'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error marking submissions as graded: {e}'))
            
        self.stdout.write(self.style.SUCCESS('Completed marking simulated submissions as graded'))

if __name__ == '__main__':
    # This allows the script to be run standalone
    from django.core.management import execute_from_command_line
    import sys
    
    execute_from_command_line(['manage.py', 'mark_submissions_graded'])