from datetime import datetime
from arango.exceptions import DocumentInsertError
from users.arangodb import db

if not db.has_collection('student_submissions'):
    db.create_collection('student_submissions')


submissions_col = db.collection('student_submissions')

def add_studentSubmission(student_id, text, grade, course_id):
    submission = {
        'student_id': student_id,
        'text': text,
        'grade': grade,
        'course_id': course_id,
        'created_at': datetime.utcnow().isoformat()
    }
    try: 
        result = submissions_col.insert(submission, overwrite = False)
        return {"success": True, "submission_id": result["_id"]}
    except DocumentInsertError as e:
        return {"success": False, "error": str(e)}


def get_submission_by_id(submission_id):
    return submissions_col.get(submission_id)

def list_submissions_for_courses(course_id):
    return list(submissions_col.find({"course_id": course_id}))

def list_submissions_by_student(student_id):
    return list(submissions_col.find({"student_id": student_id}))
