import os
import django
import json

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

# Import the database
from users.arangodb import db

def verify_network():
    print("Verifying the complete educational network...")
    
    # 1. Check collection counts
    print("\n1. Collection counts:")
    collections = ['users', 'sections', 'mistakes', 'submission', 'courses', 'rubrics']
    for collection_name in collections:
        query = f"RETURN LENGTH(FOR doc IN {collection_name} RETURN 1)"
        count = list(db.aql.execute(query))[0]
        print(f"  {collection_name}: {count} documents")
    
    # 2. Check edge collection counts
    print("\n2. Edge collection counts:")
    edge_collections = ['has_feedback_on', 'affects_criteria', 'related_to', 'made_mistake']
    for edge_name in edge_collections:
        query = f"RETURN LENGTH(FOR edge IN {edge_name} RETURN 1)"
        count = list(db.aql.execute(query))[0]
        print(f"  {edge_name}: {count} edges")
    
    # 3. Check graph structure
    print("\n3. Graph definitions:")
    graph = db.graph('educational_network')
    definitions = graph.edge_definitions()
    for def_info in definitions:
        print(f"  {def_info['edge_collection']}: {def_info['from_vertex_collections']} -> {def_info['to_vertex_collections']}")
    
    # 4. Sample data checks
    print("\n4. Sample data checks:")
    
    # Sample instructor
    query = """
    FOR u IN users
        FILTER u.role == "instructor"
        LIMIT 1
        RETURN {
            name: u.username,
            email: u.email,
            id: u._id
        }
    """
    instructors = list(db.aql.execute(query))
    if instructors:
        print(f"  Sample instructor: {instructors[0]['name']} ({instructors[0]['email']})")
    
    # Sample student
    query = """
    FOR u IN users
        FILTER u.role == "student"
        LIMIT 1
        RETURN {
            name: u.username,
            email: u.email,
            id: u._id,
            courses: u.courses
        }
    """
    students = list(db.aql.execute(query))
    if students:
        student = students[0]
        print(f"  Sample student: {student['name']} ({student['email']})")
        print(f"  Enrolled in courses: {', '.join(student['courses'])}")
    
    # Sample course
    query = """
    FOR c IN courses
        LIMIT 1
        RETURN {
            code: c.class_code,
            title: c.class_title,
            instructor_id: c.instructor_id,
            assignment_count: LENGTH(c.assignments)
        }
    """
    courses = list(db.aql.execute(query))
    if courses:
        course = courses[0]
        print(f"  Sample course: {course['code']} - {course['title']}")
        print(f"  Has {course['assignment_count']} assignments")
    
    # Sample submission
    query = """
    FOR s IN submission
        LIMIT 1
        RETURN {
            id: s._id,
            user_id: s.user_id,
            class_code: s.class_code,
            assignment_id: s.assignment_id,
            grade: s.ai_score
        }
    """
    submissions = list(db.aql.execute(query))
    if submissions:
        submission = submissions[0]
        print(f"  Sample submission: {submission['id']}")
        print(f"  By student {submission['user_id']} for {submission['class_code']}")
        print(f"  Grade: {submission['grade']}")
    
    # Sample mistake
    query = """
    FOR m IN mistakes
        LIMIT 1
        RETURN {
            id: m._id,
            question: m.question,
            score: m.score_awarded,
            assignment_id: m.assignment_id
        }
    """
    mistakes = list(db.aql.execute(query))
    if mistakes:
        mistake = mistakes[0]
        print(f"  Sample mistake: {mistake['id']}")
        print(f"  Question: {mistake['question']}")
        print(f"  Score: {mistake['score']}")
    
    # Connections
    print("\n5. Network connections:")
    query = """
    FOR edge IN has_feedback_on
        LIMIT 1
        LET submission = DOCUMENT(edge._from)
        LET mistake = DOCUMENT(edge._to)
        RETURN {
            submission_id: edge._from,
            mistake_id: edge._to,
            student_id: submission.user_id,
            question: mistake.question
        }
    """
    connections = list(db.aql.execute(query))
    if connections:
        connection = connections[0]
        print(f"  Submission {connection['submission_id']} has mistake: {connection['mistake_id']}")
        print(f"  Student: {connection['student_id']}")
        print(f"  Question: {connection['question']}")
        
        # Find related section
        query = f"""
        FOR edge IN related_to
            FILTER edge._from == '{connection['mistake_id']}'
            LET section = DOCUMENT(edge._to)
            RETURN {{
                section_id: edge._to,
                title: section.title
            }}
        """
        sections = list(db.aql.execute(query))
        if sections:
            section = sections[0]
            print(f"  Mistake is related to section: {section['title']}")
        
        # Find related rubric
        query = f"""
        FOR edge IN affects_criteria
            FILTER edge._from == '{connection['mistake_id']}'
            LET rubric = DOCUMENT(edge._to)
            RETURN {{
                rubric_id: edge._to,
                criteria: rubric.items[0].criteria
            }}
        """
        rubrics = list(db.aql.execute(query))
        if rubrics:
            rubric = rubrics[0]
            print(f"  Mistake affects rubric criteria: {rubric['criteria']}")

if __name__ == "__main__":
    verify_network()