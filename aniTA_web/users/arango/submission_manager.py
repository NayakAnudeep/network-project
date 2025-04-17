# users/arango/submission_manager.py
from users.arango.document_ops import DocumentManager
from users.arango.edge_ops import EdgeManager
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

class SubmissionManager:
    @staticmethod
    def create_submission(text, student_id, course_id, grade=None, llm_feedback=None):
        """Create a new submission with all necessary connections."""
        try:
            # Create submission document
            submission_data = {
                'text': text,
                'student_id': student_id,
                'course_id': course_id,
                'grade': grade,
                'llm_feedback': llm_feedback,
                'created_at': datetime.utcnow().isoformat()
            }
            submission = DocumentManager.create('Submissions', submission_data)
            
            # If we have a submission ID, create connections
            if submission and '_key' in submission:
                # Link to student
                EdgeManager.create(
                    'StudentSubmissions',
                    f"Students/{student_id}",
                    f"Submissions/{submission['_key']}"
                )
                
                # Link to course
                EdgeManager.create(
                    'CourseSubmissions',
                    f"Courses/{course_id}",
                    f"Submissions/{submission['_key']}"
                )
                logger.info(f"Created submission {submission['_key']} with connections")
                return submission
            
            return submission
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise
    
    @staticmethod
    def get_submission_with_mistakes(submission_id):
        """Get a submission with all its linked mistakes."""
        try:
            aql = """
            LET submission = DOCUMENT(CONCAT('Submissions/', @submission_id))
            LET mistakes = (
                FOR v, e IN 1..1 OUTBOUND submission SubmissionMistakes
                RETURN {
                    _key: v._key,
                    name: v.name,
                    description: v.description,
                    category: v.category,
                    confidence: e.confidence_score
                }
            )
            RETURN {
                submission: submission,
                mistakes: mistakes
            }
            """
            result = DocumentManager.query(aql, {'submission_id': submission_id})
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"Error retrieving submission with mistakes: {str(e)}")
            raise
    
    @staticmethod
    def link_submission_to_mistake(submission_id, mistake_id, confidence=1.0):
        """Link a submission to a mistake with a confidence score."""
        try:
            edge = EdgeManager.create(
                'SubmissionMistakes',
                f"Submissions/{submission_id}",
                f"Mistakes/{mistake_id}",
                {'confidence_score': confidence}
            )
            return edge
        except Exception as e:
            logger.error(f"Error linking submission to mistake: {str(e)}")
            raise
    
    @staticmethod
    def update_submission_grade(submission_id, grade):
        """Update a submission's grade."""
        try:
            DocumentManager.update('Submissions', submission_id, {'grade': grade})
            logger.info(f"Updated grade for submission {submission_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating submission grade: {str(e)}")
            raise
            
    @staticmethod
    def get_student_submissions(student_id, limit=20):
        """Get all submissions for a student with their associated grades and courses."""
        try:
            aql = """
            FOR s IN Submissions
                FILTER s.student_id == @student_id
                SORT s.created_at DESC
                LIMIT @limit
                LET course = DOCUMENT(CONCAT('Courses/', s.course_id))
                LET mistake_count = LENGTH(
                    FOR v IN 1..1 OUTBOUND s SubmissionMistakes
                    RETURN v
                )
                RETURN {
                    _key: s._key,
                    text: s.text,
                    grade: s.grade,
                    created_at: s.created_at,
                    course_name: course.name,
                    course_id: s.course_id,
                    mistake_count: mistake_count
                }
            """
            result = DocumentManager.query(aql, {
                'student_id': student_id,
                'limit': limit
            })
            return result
        except Exception as e:
            logger.error(f"Error retrieving student submissions: {str(e)}")
            raise
            
    @staticmethod
    def get_course_submissions(course_id, limit=50):
        """Get all submissions for a course with grade statistics."""
        try:
            aql = """
            LET submissions = (
                FOR s IN Submissions
                FILTER s.course_id == @course_id
                SORT s.created_at DESC
                LIMIT @limit
                LET student = DOCUMENT(CONCAT('Students/', s.student_id))
                LET mistake_count = LENGTH(
                    FOR v IN 1..1 OUTBOUND s SubmissionMistakes
                    RETURN v
                )
                RETURN {
                    _key: s._key,
                    student_name: student.username,
                    student_id: s.student_id,
                    grade: s.grade,
                    created_at: s.created_at,
                    mistake_count: mistake_count
                }
            )
            
            LET stats = (
                FOR s IN submissions
                COLLECT AGGREGATE 
                    count = COUNT(),
                    avg_grade = AVERAGE(s.grade),
                    min_grade = MIN(s.grade),
                    max_grade = MAX(s.grade)
                RETURN {
                    count: count,
                    avg_grade: avg_grade,
                    min_grade: min_grade,
                    max_grade: max_grade
                }
            )
            
            RETURN {
                submissions: submissions,
                stats: stats[0]
            }
            """
            result = DocumentManager.query(aql, {
                'course_id': course_id,
                'limit': limit
            })
            if result and len(result) > 0:
                return result[0]
            return {'submissions': [], 'stats': {}}
        except Exception as e:
            logger.error(f"Error retrieving course submissions: {str(e)}")
            raise
            
    @staticmethod
    def add_llm_feedback(submission_id, feedback):
        """Add or update LLM feedback for a submission."""
        try:
            DocumentManager.update('Submissions', submission_id, {
                'llm_feedback': feedback,
                'feedback_added_at': datetime.utcnow().isoformat()
            })
            logger.info(f"Added LLM feedback for submission {submission_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding LLM feedback: {str(e)}")
            raise
