
from users.arangodb import db  # Reusing your ArangoDB connection

# Ensure all edge collections exist
edge_collections = {
    "submission_mistakes": ("student_submissions", "mistakes"),
    "mistake_feedback": ("mistakes", "feedbacks"),
    "rubric_mistake": ("rubrics", "mistakes"),
    "submission_rubric": ("student_submissions", "rubrics"),
    "course_submission": ("courses", "student_submissions"),
    "instructor_course": ("instructors", "courses")
}

for edge_col, (from_col, to_col) in edge_collections.items():
    if not db.has_collection(edge_col):
        db.create_collection(edge_col, edge=True)

# Shortcut to get any edge collection
def _get_edge_collection(name):
    return db.collection(name)

# General-purpose function
def link_nodes(edge_collection, from_id, to_id, attributes=None):
    """Create an edge between two documents."""
    edge_doc = {"_from": from_id, "_to": to_id}
    if attributes:
        edge_doc.update(attributes)
    edge_col = _get_edge_collection(edge_collection)
    return edge_col.insert(edge_doc)

# Specific edge functions
def link_submission_to_mistake(sub_id, mistake_id):
    return link_nodes("submission_mistakes", sub_id, mistake_id)

def link_mistake_to_feedback(mistake_id, feedback_id):
    return link_nodes("mistake_feedback", mistake_id, feedback_id)

def link_rubric_to_mistake(rubric_id, mistake_id):
    return link_nodes("rubric_mistake", rubric_id, mistake_id)

def link_submission_to_rubric(sub_id, rubric_id):
    return link_nodes("submission_rubric", sub_id, rubric_id)

def link_course_to_submission(course_id, sub_id):
    return link_nodes("course_submission", course_id, sub_id)

def link_instructor_to_course(instr_id, course_id):
    return link_nodes("instructor_course", instr_id, course_id)
