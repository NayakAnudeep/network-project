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
