
from datetime import datetime
from users.arangodb import db

# Ensure the 'questions' collection exists
if not db.has_collection("questions"):
    db.create_collection("questions")

questions_col = db.collection("questions")

def add_question(text, course_id, instructor_id):
    """Insert a new question into the questions collection."""
    question = {
        "text": text,
        "course_id": course_id,
        "instructor_id": instructor_id,
        "created_at": datetime.utcnow().isoformat()
    }
    result = questions_col.insert(question)
    return {"success": True, "question_id": result["_id"]}


def get_question_by_id(question_id):
    """Retrieve a question by _id."""
    return questions_col.get(question_id)


def list_questions_for_course(course_id):
    """Get all questions for a given course."""
    return list(questions_col.find({"course_id": course_id}))


def list_questions_by_instructor(instructor_id):
    """Get all questions created by a specific instructor."""
    return list(questions_col.find({"instructor_id": instructor_id}))

