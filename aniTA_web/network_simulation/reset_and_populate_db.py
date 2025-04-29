"""
Reset and Populate Database

This script clears the existing simulated data from the database 
and repopulates it with realistic data.
"""

import os
import django
import sys
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from users.arangodb import db
from network_simulation.realistic_data_generator import regenerate_data
from network_simulation.import_to_arango import import_network_to_arango

def reset_database():
    """Clear and reset the database."""
    print(f"Starting database reset at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check database connection
    try:
        db_info = db.properties()
        print(f"Connected to database: {db_info['name']}")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
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
            print(f"Creating collection: {name}")
            if is_edge:
                db.create_collection(name, edge=True)
            else:
                db.create_collection(name)
        else:
            print(f"Collection {name} already exists")
    
    # 3. Import network data if needed
    users_count = len(list(db.collection('users').all()))
    courses_count = len(list(db.collection('courses').all()))
    
    if users_count == 0 or courses_count == 0:
        print("Database is empty, importing base network data...")
        json_file = "network_data.json"
        csv_dir = "csv_data"
        
        if not os.path.exists(json_file):
            print(f"Error: {json_file} not found. Please run generate_data.py first.")
            sys.exit(1)
        
        results = import_network_to_arango(json_file, csv_dir)
        print(f"Imported data: {results}")
    else:
        print(f"Found {users_count} users and {courses_count} courses in the database.")
    
    # 4. Generate realistic data
    print("Regenerating realistic data with questions, answers, rubrics, and feedback...")
    results = regenerate_data()
    
    print("\nData regeneration completed successfully!")
    print(f"Generated {results['submission_count']} realistic submissions across {results['course_count']} courses.")
    print("The database now contains:")
    
    # Print stats
    for collection_name in collections:
        count = len(list(db.collection(collection_name).all()))
        print(f"- {collection_name}: {count} documents")
    
    # Check for rubric connections
    rubric_connection_query = """
    FOR edge IN affects_criteria
        RETURN edge
    """
    rubric_connections = len(list(db.aql.execute(rubric_connection_query)))
    print(f"- Feedback-to-rubric connections: {rubric_connections}")
    
    material_connection_query = """
    FOR edge IN related_to
        FILTER STARTS_WITH(edge._from, "rubrics/")
        RETURN edge
    """
    material_connections = len(list(db.aql.execute(material_connection_query)))
    print(f"- Rubric-to-material connections: {material_connections}")
    
    print(f"\nDatabase reset completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    reset_database()