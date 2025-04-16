# users/arango/graph_manager.py
from users.arangodb import db
import logging

logger = logging.getLogger(__name__)

def initialize_knowledge_graph_collections():
    """Initialize all collections needed for the knowledge graph."""
    # Document collections
    collections = [
        'Students', 'Submissions', 'Mistakes', 
        'Feedback', 'Rubrics', 'Instructors', 'Courses'
    ]
    
    # Edge collections
    edge_collections = [
        'SubmissionMistakes', 'MistakeFeedback', 'RubricMistakes',
        'SubmissionGrades', 'CourseSubmissions', 'InstructorCourses',
        'StudentSubmissions'
    ]
    
    # Create document collections
    for collection_name in collections:
        if not db.has_collection(collection_name):
            db.create_collection(collection_name)
            logger.info(f"Created document collection: {collection_name}")
    
    # Create edge collections
    for collection_name in edge_collections:
        if not db.has_collection(collection_name):
            db.create_collection(collection_name, edge=True)
            logger.info(f"Created edge collection: {collection_name}")
    
    # Create indexes
    if db.has_collection('Submissions'):
        submissions = db.collection('Submissions')
        if not any(idx.get('fields') == ['student_id'] for idx in submissions.indexes()):
            submissions.add_hash_index(['student_id'])
            logger.info("Created index on Submissions.student_id")
        
        if not any(idx.get('fields') == ['course_id'] for idx in submissions.indexes()):
            submissions.add_hash_index(['course_id'])
            logger.info("Created index on Submissions.course_id")

def initialize_graph():
    """Initialize the AI TA knowledge graph."""
    graph_name = 'ai_ta_graph'
    
    if not db.has_graph(graph_name):
        graph = db.create_graph(graph_name)
        logger.info(f"Created graph: {graph_name}")
        
        # Define edge relationships
        edge_definitions = [
            {
                'edge_collection': 'SubmissionMistakes',
                'from_vertex_collections': ['Submissions'],
                'to_vertex_collections': ['Mistakes']
            },
            {
                'edge_collection': 'MistakeFeedback',
                'from_vertex_collections': ['Mistakes'],
                'to_vertex_collections': ['Feedback']
            },
            {
                'edge_collection': 'RubricMistakes',
                'from_vertex_collections': ['Rubrics'],
                'to_vertex_collections': ['Mistakes']
            },
            {
                'edge_collection': 'SubmissionGrades',
                'from_vertex_collections': ['Submissions'],
                'to_vertex_collections': ['Rubrics']
            },
            {
                'edge_collection': 'CourseSubmissions',
                'from_vertex_collections': ['Courses'],
                'to_vertex_collections': ['Submissions']
            },
            {
                'edge_collection': 'InstructorCourses',
                'from_vertex_collections': ['Instructors'],
                'to_vertex_collections': ['Courses']
            },
            {
                'edge_collection': 'StudentSubmissions',
                'from_vertex_collections': ['Students'],
                'to_vertex_collections': ['Submissions']
            }
        ]
        
        # Add edge definitions to graph
        for edge_def in edge_definitions:
            graph.create_edge_definition(
                edge_collection=edge_def['edge_collection'],
                from_vertex_collections=edge_def['from_vertex_collections'],
                to_vertex_collections=edge_def['to_vertex_collections']
            )
            logger.info(f"Added edge definition: {edge_def['edge_collection']}")
    else:
        logger.info(f"Graph {graph_name} already exists")

def setup_knowledge_graph():
    """Set up the complete knowledge graph structure."""
    initialize_knowledge_graph_collections()
    initialize_graph()
    logger.info("Knowledge graph setup complete")



def is_db_connected():
    """Check if the database connection is working."""
    try:
        # Try to get server version to test connection
        db.properties()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

def safe_setup_knowledge_graph():
    """Set up the knowledge graph with connection retry."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if is_db_connected():
                setup_knowledge_graph()
                return True
            else:
                logger.warning("Database not connected, retrying...")
                retry_count += 1
                time.sleep(2)  # Wait 2 seconds before retry
        except Exception as e:
            logger.error(f"Error setting up knowledge graph: {str(e)}")
            retry_count += 1
            time.sleep(2)  # Wait 2 seconds before retry
    
    logger.error("Failed to set up knowledge graph after maximum retries")
    return False
