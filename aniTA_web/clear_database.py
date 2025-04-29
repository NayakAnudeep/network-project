import os
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import the database
from users.arangodb import db

# Collections to clear
collections = [
    'users', 'sections', 'mistakes', 'relevant_chunks', 'submission', 
    'courses', 'course_materials', 'rubrics', 'material_vectors', 
    'material_questions', 'NetworkData'
]

# Edge collections to clear
edge_collections = [
    'has_feedback_on', 'affects_criteria', 'made_mistake', 'related_to',
    'has_rubric', 'has_material', 'has_question'
]

# Clear all collections
for collection_name in collections:
    try:
        if db.has_collection(collection_name):
            collection = db.collection(collection_name)
            collection.truncate()
            print(f"Cleared collection: {collection_name}")
    except Exception as e:
        print(f"Error clearing collection {collection_name}: {e}")

# Clear all edge collections
for edge_name in edge_collections:
    try:
        if db.has_collection(edge_name):
            edge = db.collection(edge_name)
            edge.truncate()
            print(f"Cleared edge collection: {edge_name}")
    except Exception as e:
        print(f"Error clearing edge collection {edge_name}: {e}")

print("Database cleared successfully")