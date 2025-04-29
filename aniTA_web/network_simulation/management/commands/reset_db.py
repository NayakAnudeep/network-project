from django.core.management.base import BaseCommand
from network_simulation.realistic_data_generator import regenerate_data
from users.arangodb import db
import logging

class Command(BaseCommand):
    help = 'Reset and repopulate ArangoDB with realistic data'

    def handle(self, *args, **options):
        self.stdout.write("Starting database reset and repopulation...")
        
        # 1. Check database connection
        try:
            db_info = db.properties()
            self.stdout.write(f"Connected to database: {db_info['name']}")
        except Exception as e:
            self.stderr.write(f"Error connecting to database: {e}")
            return
        
        # 2. Check collections
        collections = {
            "users": False,
            "courses": False,
            "submission": False,
            "mistakes": False,
            "rubrics": False,
            "course_materials": False,
            "made_mistake": True,  # True indicates edge collection
            "affects_criteria": True,
            "related_to": True,
            "has_feedback_on": True,
            "has_rubric": True,
            "has_material": True
        }
        
        for name, is_edge in collections.items():
            if not db.has_collection(name):
                self.stdout.write(f"Creating collection: {name}")
                if is_edge:
                    db.create_collection(name, edge=True)
                else:
                    db.create_collection(name)
            else:
                self.stdout.write(f"Collection {name} already exists")
        
        # 3. Clear existing simulated data
        self.stdout.write("Clearing existing simulated data...")
        try:
            # Clear the relevant collections
            collections_to_clear = [
                'submission', 'mistakes', 'made_mistake', 'affects_criteria', 
                'related_to', 'has_feedback_on', 'course_materials', 'rubrics',
                'has_rubric', 'has_material'
            ]
            
            for collection_name in collections_to_clear:
                if db.has_collection(collection_name):
                    # For edge collections, delete edges to avoid orphans
                    if db.collection(collection_name).properties().get('edge', False):
                        db.aql.execute(f"""
                        FOR edge IN {collection_name}
                            REMOVE edge IN {collection_name}
                        """)
                    else:
                        # For document collections, clear all documents
                        db.aql.execute(f"""
                        FOR doc IN {collection_name}
                            REMOVE doc IN {collection_name}
                        """)
                    
                    self.stdout.write(f"Cleared collection: {collection_name}")
            
        except Exception as e:
            self.stderr.write(f"Error clearing data: {e}")
        
        # 4. Generate realistic data
        self.stdout.write("Regenerating realistic data with questions, answers, rubrics, and feedback...")
        
        try:
            results = regenerate_data()
            self.stdout.write(f"Data regeneration completed successfully!")
            self.stdout.write(f"Generated {results['submission_count']} realistic submissions across {results['course_count']} courses.")
            
            # Print stats
            for collection_name in collections:
                count = len(list(db.collection(collection_name).all()))
                self.stdout.write(f"- {collection_name}: {count} documents")
            
            # Check for rubric connections
            rubric_connection_query = """
            FOR edge IN affects_criteria
                RETURN edge
            """
            rubric_connections = len(list(db.aql.execute(rubric_connection_query)))
            self.stdout.write(f"- Feedback-to-rubric connections: {rubric_connections}")
            
            material_connection_query = """
            FOR edge IN related_to
                FILTER STARTS_WITH(edge._from, "rubrics/")
                RETURN edge
            """
            material_connections = len(list(db.aql.execute(material_connection_query)))
            self.stdout.write(f"- Rubric-to-material connections: {material_connections}")
        
        except Exception as e:
            self.stderr.write(f"Error regenerating data: {e}")