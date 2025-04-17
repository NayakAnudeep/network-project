# users/arango/algorithms.py
from users.arango.document_ops import DocumentManager
import logging

logger = logging.getLogger(__name__)

class JaccardSimilarity:
    @staticmethod
    def calculate_similarity(submission_id1, submission_id2):
        """Calculate Jaccard similarity between two submissions' mistakes."""
        try:
            aql = """
            LET submission1_mistakes = (
                FOR v, e IN 1..1 OUTBOUND CONCAT('Submissions/', @submission_id1) SubmissionMistakes
                RETURN v._key
            )
            
            LET submission2_mistakes = (
                FOR v, e IN 1..1 OUTBOUND CONCAT('Submissions/', @submission_id2) SubmissionMistakes
                RETURN v._key
            )
            
            LET intersection = LENGTH(INTERSECTION(submission1_mistakes, submission2_mistakes))
            LET union = LENGTH(UNION(submission1_mistakes, submission2_mistakes))
            
            RETURN {
                similarity: union > 0 ? intersection / union : 0,
                submission1_id: @submission_id1,
                submission2_id: @submission_id2,
                submission1_mistakes: submission1_mistakes,
                submission2_mistakes: submission2_mistakes
            }
            """
            
            result = DocumentManager.query(aql, {
                'submission_id1': submission_id1, 
                'submission_id2': submission_id2
            })
            
            if result and len(result) > 0:
                return result[0]
            return {'similarity': 0}
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise

    @staticmethod
    def find_similar_submissions(submission_id, threshold=0.6, limit=5):
        """Find submissions similar to the given one."""
        try:
            aql = """
            LET target = DOCUMENT(CONCAT('Submissions/', @submission_id))
            LET target_mistakes = (
                FOR v, e IN 1..1 OUTBOUND target SubmissionMistakes
                RETURN v._key
            )
            
            LET similar_submissions = (
                FOR s IN Submissions
                FILTER s._key != @submission_id
                
                LET s_mistakes = (
                    FOR v, e IN 1..1 OUTBOUND s SubmissionMistakes
                    RETURN v._key
                )
                
                LET intersection = LENGTH(INTERSECTION(target_mistakes, s_mistakes))
                LET union = LENGTH(UNION(target_mistakes, s_mistakes))
                LET similarity = union > 0 ? intersection / union : 0
                
                FILTER similarity >= @threshold
                
                SORT similarity DESC
                LIMIT @limit
                
                RETURN {
                    _key: s._key,
                    grade: s.grade,
                    student_id: s.student_id,
                    similarity: similarity,
                    matching_mistakes: INTERSECTION(target_mistakes, s_mistakes)
                }
            )
            
            RETURN {
                submission_id: @submission_id,
                similar_submissions: similar_submissions
            }
            """
            
            result = DocumentManager.query(aql, {
                'submission_id': submission_id,
                'threshold': threshold,
                'limit': limit
            })
            
            if result and len(result) > 0:
                return result[0]
            return {'submission_id': submission_id, 'similar_submissions': []}
        except Exception as e:
            logger.error(f"Error finding similar submissions: {str(e)}")
            raise

    @staticmethod
    def check_grading_consistency(submission_id, threshold=0.6, grade_diff_threshold=2):
        """Check if the grading is consistent with similar submissions."""
        try:
            aql = """
            LET target = DOCUMENT(CONCAT('Submissions/', @submission_id))
            LET target_mistakes = (
                FOR v, e IN 1..1 OUTBOUND target SubmissionMistakes
                RETURN v._key
            )
            
            LET similar_submissions = (
                FOR s IN Submissions
                FILTER s._key != @submission_id
                
                LET s_mistakes = (
                    FOR v, e IN 1..1 OUTBOUND s SubmissionMistakes
                    RETURN v._key
                )
                
                LET intersection = LENGTH(INTERSECTION(target_mistakes, s_mistakes))
                LET union = LENGTH(UNION(target_mistakes, s_mistakes))
                LET similarity = union > 0 ? intersection / union : 0
                
                FILTER similarity >= @threshold
                
                SORT similarity DESC
                LIMIT 10
                
                RETURN {
                    _key: s._key,
                    grade: s.grade,
                    similarity: similarity,
                    grade_diff: ABS(s.grade - target.grade),
                    matching_mistakes: INTERSECTION(target_mistakes, s_mistakes)
                }
            )
            
            LET inconsistencies = (
                FOR s IN similar_submissions
                FILTER s.grade_diff > @grade_diff_threshold
                RETURN s
            )
            
            RETURN {
                submission_id: @submission_id,
                grade: target.grade,
                similar_submissions: similar_submissions,
                inconsistencies: inconsistencies,
                is_consistent: LENGTH(inconsistencies) == 0
            }
            """
            
            result = DocumentManager.query(aql, {
                'submission_id': submission_id,
                'threshold': threshold,
                'grade_diff_threshold': grade_diff_threshold
            })
            
            if result and len(result) > 0:
                return result[0]
            return {'is_consistent': True, 'inconsistencies': []}
        except Exception as e:
            logger.error(f"Error checking grading consistency: {str(e)}")
            raise

class ClusteringAlgorithms:
    @staticmethod
    def cluster_submissions_by_mistakes(course_id, threshold=0.6):
        """Cluster submissions based on similar mistakes."""
        try:
            aql = """
            // Get all submissions for the course
            LET course_submissions = (
                FOR s IN Submissions
                FILTER s.course_id == @course_id
                RETURN s._key
            )
            
            // Create clusters using similarity
            LET clusters = (
                LET visited = []
                LET result = []
                
                FOR s1 IN course_submissions
                    FILTER s1 NOT IN visited
                    
                    LET cluster = (
                        FOR s2 IN course_submissions
                            FILTER s2 != s1
                            
                            LET s1_mistakes = (
                                FOR v IN 1..1 OUTBOUND CONCAT('Submissions/', s1) SubmissionMistakes
                                RETURN v._key
                            )
                            
                            LET s2_mistakes = (
                                FOR v IN 1..1 OUTBOUND CONCAT('Submissions/', s2) SubmissionMistakes
                                RETURN v._key
                            )
                            
                            LET intersection = LENGTH(INTERSECTION(s1_mistakes, s2_mistakes))
                            LET union = LENGTH(UNION(s1_mistakes, s2_mistakes))
                            LET similarity = union > 0 ? intersection / union : 0
                            
                            FILTER similarity >= @threshold
                            
                            // Mark as visited
                            LET _ = PUSH(visited, s2)
                            
                            RETURN s2
                    )
                    
                    // Include the seed submission in the cluster
                    LET full_cluster = APPEND([s1], cluster)
                    
                    // Only add non-empty clusters
                    FILTER LENGTH(full_cluster) > 1
                    
                    // Mark seed as visited
                    LET _ = PUSH(visited, s1)
                    
                    // Get common mistakes for this cluster
                    LET all_mistakes = (
                        FOR sub IN full_cluster
                            FOR v IN 1..1 OUTBOUND CONCAT('Submissions/', sub) SubmissionMistakes
                            RETURN v._key
                    )
                    
                    LET common_mistakes = (
                        FOR m IN all_mistakes
                            COLLECT mistake = m WITH COUNT INTO freq
                            FILTER freq >= LENGTH(full_cluster) * 0.7
                            RETURN mistake
                    )
                    
                    RETURN {
                        submissions: full_cluster,
                        size: LENGTH(full_cluster),
                        common_mistakes: common_mistakes
                    }
            )
            
            RETURN clusters
            """
            
            result = DocumentManager.query(aql, {
                'course_id': course_id,
                'threshold': threshold
            })
            
            return result[0] if result else {'clusters': []}
        except Exception as e:
            logger.error(f"Error clustering submissions: {str(e)}")
            raise

class PageRankAlgorithms:
    @staticmethod
    def get_most_common_mistakes(course_id, limit=10):
        """Get the most common mistakes for a course."""
        try:
            aql = """
            // Get all submissions for the course
            LET submissions = (
                FOR s IN Submissions
                FILTER s.course_id == @course_id
                RETURN s._id
            )
            
            // Count occurrences of each mistake
            LET mistake_counts = (
                FOR s IN submissions
                    FOR v, e IN 1..1 OUTBOUND s SubmissionMistakes
                    
                    COLLECT mistake = v WITH COUNT INTO freq
                    
                    LET mistake_doc = DOCUMENT(v._id)
                    
                    RETURN {
                        _key: mistake_doc._key,
                        name: mistake_doc.name,
                        category: mistake_doc.category,
                        description: mistake_doc.description,
                        frequency: freq
                    }
            )
            
            // Sort by frequency
            FOR m IN mistake_counts
                SORT m.frequency DESC
                LIMIT @limit
                RETURN m
            """
            
            result = DocumentManager.query(aql, {
                'course_id': course_id,
                'limit': limit
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting most common mistakes: {str(e)}")
            raise

    @staticmethod
    def get_most_relevant_feedback(mistake_id):
        """Get the most relevant feedback for a mistake."""
        try:
            aql = """
            // Get all feedback for this mistake
            LET feedbacks = (
                FOR f, e IN 1..1 OUTBOUND CONCAT('Mistakes/', @mistake_id) MistakeFeedback
                SORT e.relevance_score DESC
                RETURN {
                    _key: f._key,
                    message: f.message,
                    relevance: e.relevance_score
                }
            )
            
            RETURN feedbacks
            """
            
            result = DocumentManager.query(aql, {
                'mistake_id': mistake_id
            })
            
            return result
        except Exception as e:
            logger.error(f"Error getting feedback for mistake: {str(e)}")
            raise
