from users.arangodb import db
from datetime import datetime

def find_section_for_chunk(assignment_id, chunk_text):
    """
    Given a chunk of text, find the best matching Section from the DB.
    """
    sections = list(db.collection('sections').find({
        "assignment_id": assignment_id
    }))

    best_match = None
    max_overlap = 0

    chunk_words = set(chunk_text.lower().split())

    for section in sections:
        section_words = set(section["content"].lower().split())
        overlap = len(chunk_words.intersection(section_words))
        
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = section

    if best_match:
        return best_match["_id"]
    else:
        return None

def store_mistake_and_edges(student_id, submission_id, assignment_id, result_item, relevant_chunks, rubric_mapping):
    """
    Store a Mistake node and link it to the appropriate Section based on relevant chunks.
    """
    mistakes = db.collection('mistakes')
    has_feedback_on = db.collection('has_feedback_on')
    made_mistake = db.collection('made_mistake')
    affects_criteria = db.collection('affects_criteria')
    related_to = db.collection('related_to')

    # 1. Create mistake node
    mistake_doc = {
        "assignment_id": assignment_id,
        "question": result_item.get("question", ""),
        "justification": result_item.get("justification", ""),
        "score_awarded": result_item.get("score", 0),
        "rubric_criteria_names": [rc["criteria"] for rc in result_item.get("rubric_criteria", [])],
        "created_at": datetime.utcnow().isoformat()
    }
    mistake_meta = mistakes.insert(mistake_doc)
    mistake_id = mistake_meta["_id"]

    # 2. Edge: Submission --> Mistake
    has_feedback_on.insert({
        "_from": f"submission/{submission_id}",
        "_to": mistake_id
    })

    # 3. Edge: Student --> Mistake
    made_mistake.insert({
        "_from": student_id,
        "_to": mistake_id
    })

    # 4. Edge: Mistake --> Rubric
    for rubric_name in mistake_doc["rubric_criteria_names"]:
        rubric_id = rubric_mapping.get(rubric_name)
        if rubric_id:
            affects_criteria.insert({
                "_from": mistake_id,
                "_to": rubric_id
            })

    # 5. 🔥 Edge: Mistake --> Section
    for chunk_text in relevant_chunks:
        section_id = find_section_for_chunk(assignment_id, chunk_text)
        if section_id:
            related_to.insert({
                "_from": mistake_id,
                "_to": section_id
            })

    return mistake_id
