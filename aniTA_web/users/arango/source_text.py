
from datetime import datetime
from users.arangodb import db

# Ensure the 'source_texts' collection exists
if not db.has_collection("source_texts"):
    db.create_collection("source_texts")

source_col = db.collection("source_texts")

def add_source_text(text, topic, course_id, embedding=None):
    """Insert a new source text."""
    doc = {
        "text": text,
        "topic": topic,
        "course_id": course_id,
        "created_at": datetime.utcnow().isoformat()
    }
    if embedding:
        doc["embedding"] = embedding
    result = source_col.insert(doc)
    return {"success": True, "source_id": result["_id"]}


def get_source_by_id(source_id):
    """Retrieve a source text by _id."""
    return source_col.get(source_id)


def list_sources_for_topic(topic):
    """List all source texts for a given topic."""
    return list(source_col.find({"topic": topic}))


def list_sources_for_course(course_id):
    """List all source texts linked to a course."""
    return list(source_col.find({"course_id": course_id}))
