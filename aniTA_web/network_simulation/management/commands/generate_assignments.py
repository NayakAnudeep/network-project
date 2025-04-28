from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time

from network_simulation.claude_integration import (
    create_simulated_assignment_workflow,
    rank_sections_by_pagerank
)

class Command(BaseCommand):
    help = 'Generate simulated assignments with source materials and Claude-powered feedback'

    def add_arguments(self, parser):
        parser.add_argument('--courses', type=int, default=3,
                            help='Number of courses to generate assignments for')
        parser.add_argument('--students', type=int, default=5,
                            help='Number of students per assignment')
        parser.add_argument('--delay', type=int, default=2,
                            help='Delay between Claude API calls in seconds')

    def handle(self, *args, **options):
        # Check if Claude API key is available
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        if not api_key:
            self.stdout.write(self.style.ERROR(
                'Anthropic API key not found. Set ANTHROPIC_API_KEY in settings.py or as an environment variable.'
            ))
            return
        
        num_courses = options['courses']
        num_students = options['students']
        delay = options['delay']
        
        # Course topics pairs (course name, topic)
        course_topics = [
            ("Introduction to Computer Science", "Algorithms and Problem Solving"),
            ("Data Structures and Algorithms", "Graph Traversal Techniques"),
            ("Database Systems", "Relational Database Normalization"),
            ("Computer Networks", "TCP/IP Protocol Suite"),
            ("Machine Learning", "Supervised vs Unsupervised Learning"),
            ("Software Engineering", "Agile Development Methodologies")
        ]
        
        # Limit to the number of courses requested
        course_topics = course_topics[:num_courses]
        
        self.stdout.write(self.style.SUCCESS(f'Generating assignments for {len(course_topics)} courses with {num_students} students each...'))
        
        results = []
        for course_name, topic in course_topics:
            self.stdout.write(f'Processing {course_name} - {topic}...')
            
            try:
                # Create the assignment workflow
                result = create_simulated_assignment_workflow(course_name, topic, num_students)
                
                if result:
                    results.append({
                        "course": course_name,
                        "topic": topic,
                        "result": result
                    })
                    self.stdout.write(self.style.SUCCESS(f'  Successfully created assignment for {course_name}'))
                else:
                    self.stdout.write(self.style.ERROR(f'  Failed to create assignment for {course_name}'))
                
                # Delay between Claude API calls to avoid rate limits
                time.sleep(delay)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error processing {course_name}: {str(e)}'))
        
        # Run PageRank to rank all sections
        self.stdout.write('Ranking sections using PageRank algorithm...')
        try:
            pagerank_results = rank_sections_by_pagerank()
            self.stdout.write(self.style.SUCCESS(f'  Successfully ranked {len(pagerank_results)} sections'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error ranking sections: {str(e)}'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\nSummary:'))
        self.stdout.write(f'Created {len(results)} assignments with source materials and feedback')
        for res in results:
            self.stdout.write(f'  - {res["course"]}: {res["topic"]} ({len(res["result"]["submission_ids"])} submissions)')