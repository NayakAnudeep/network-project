from django.core.management.base import BaseCommand
import logging
from network_simulation.generate_network_data import (
    generate_student_instructor_network,
    generate_course_network,
    generate_student_performance_data
)

class Command(BaseCommand):
    help = 'Generates network data for visualizations and stores it in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting network data generation...')
        
        try:
            # Generate student-instructor network
            self.stdout.write('Generating student-instructor network data...')
            student_instructor_data = generate_student_instructor_network()
            self.stdout.write(self.style.SUCCESS('✅ Student-instructor network data generated and stored successfully.'))
            
            # Generate course network
            self.stdout.write('Generating course network data...')
            course_network_data = generate_course_network()
            self.stdout.write(self.style.SUCCESS('✅ Course network data generated and stored successfully.'))
            
            # Generate student performance data
            self.stdout.write('Generating student performance data...')
            student_performance_data = generate_student_performance_data()
            self.stdout.write(self.style.SUCCESS('✅ Student performance data generated and stored successfully.'))
            
            self.stdout.write(self.style.SUCCESS('All network data generated and stored successfully!'))
            
        except Exception as e:
            logging.error(f"Error generating network data: {str(e)}")
            self.stdout.write(self.style.ERROR(f'❌ Error generating network data: {str(e)}'))
            raise e