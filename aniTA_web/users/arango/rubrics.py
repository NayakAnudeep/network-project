
from users.arangodb import db  # using your existing ArangoDB connection
from datetime import datetime
from arango.exceptions import DocumentInsertError

# Ensure necessary collections exist
for collection_name in ["rubrics", "mistakes", "feedbacks"]:
    if not db.has_collection(collection_name):
        db.create_collection(collection_name)

rubrics_col = db.collection("rubrics")
mistakes_col = db.collection("mistakes")
feedbacks_col = db.collection("feedbacks")


def add_rubric(criterion, weight, category):
    """Insert a new rubric item."""
    rubric = {
        "criterion": criterion,
        "weight": weight,
        "category": category,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        result = rubrics_col.insert(rubric, overwrite=False)
        return {"success": True, "rubric_id": result["_id"]}
    except DocumentInsertError as e:
        return {"success": False, "error": str(e)}


def add_mistake(name, description):
    """Insert a new mistake category."""
    mistake = {
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        result = mistakes_col.insert(mistake, overwrite=False)
        return {"success": True, "mistake_id": result["_id"]}
    except DocumentInsertError as e:
        return {"success": False, "error": str(e)}


def add_feedback(message, linked_mistake_id=None):
    """Insert feedback, optionally linking it to a mistake."""
    feedback = {
        "message": message,
        "linked_mistake_id": linked_mistake_id,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        result = feedbacks_col.insert(feedback, overwrite=False)
        return {"success": True, "feedback_id": result["_id"]}
    except DocumentInsertError as e:
        return {"success": False, "error": str(e)}
