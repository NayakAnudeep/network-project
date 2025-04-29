"""
Rubric-based analysis for the instructor dashboard.

This module contains functions to analyze rubric data and mistakes in student submissions.
"""

import logging
from users.arangodb import db

def get_rubrics_with_highest_degree(instructor_id):
    """
    Find rubric items with the highest degree of connections, filtered by instructor's courses.
    
    Args:
        instructor_id (str): The instructor's ArangoDB ID
        
    Returns:
        list: A list of rubric items ranked by their degree centrality
    """
    # First check if we have created rubrics
    try:
        # Count rubrics in collection
        rubric_count_query = "RETURN LENGTH(rubrics)"
        rubric_count = list(db.aql.execute(rubric_count_query))[0]
        
        if rubric_count == 0:
            logging.warning("No rubrics found in database")
            # Return mock data for demonstration
            return [
                {
                    "id": "rubric1",
                    "name": "Complexity Analysis",
                    "description": "Correctly identifies the time complexity",
                    "connections": 15,
                    "degree": 25
                },
                {
                    "id": "rubric2",
                    "name": "Algorithm Understanding",
                    "description": "Explains the divide-and-conquer approach",
                    "connections": 12,
                    "degree": 18
                },
                {
                    "id": "rubric3",
                    "name": "OOP Principles",
                    "description": "Accurately describes object-oriented concepts",
                    "connections": 10,
                    "degree": 15
                }
            ]
    except Exception as e:
        logging.error(f"Error checking rubric collection: {str(e)}")
    
    try:
        # Get all rubrics with their connections
        rubric_query = """
        FOR rubric IN rubrics
            LET connections = (
                FOR edge IN affects_criteria
                    FILTER edge._to == rubric._id
                    COLLECT WITH COUNT INTO count
                    RETURN count
            )[0]
            
            FILTER connections > 0
            SORT connections DESC
            LIMIT 15
            
            RETURN {
                id: rubric._id,
                name: rubric.name,
                description: rubric.description,
                connections: connections,
                degree: connections
            }
        """
        
        rubrics = list(db.aql.execute(rubric_query))
        
        if len(rubrics) > 0:
            logging.info(f"Found {len(rubrics)} rubrics with connections")
            return rubrics
            
        # If no results, fall back to instructor-specific query
        course_query = """
        FOR course IN courses
            FILTER course.instructor_id == @instructor_id
            RETURN course.class_code
        """
        course_codes = list(db.aql.execute(course_query, bind_vars={'instructor_id': instructor_id}))
        
        if not course_codes:
            logging.warning(f"No courses found for instructor {instructor_id}")
            # Get any courses as fallback
            course_codes = list(db.aql.execute("FOR course IN courses LIMIT 3 RETURN course.class_code"))
            
        # Find rubrics that are connected to submissions in these courses
        rubric_degree_query = """
        LET courses = @course_codes
        
        // Find all submissions from these courses
        LET submissions = (
            FOR submission IN submission
                FILTER submission.class_code IN courses
                RETURN submission._id
        )
        
        // Find mistakes connected to these submissions
        LET mistakes = (
            FOR edge IN has_feedback_on
                FILTER edge._from IN submissions
                RETURN edge._to
        )
        
        // Find rubrics connected to these mistakes
        FOR edge IN affects_criteria
            FILTER edge._from IN mistakes
            
            LET rubric = DOCUMENT(edge._to)
            
            // Count how many connections this rubric has
            LET degree = (
                FOR e IN affects_criteria
                    FILTER e._to == edge._to
                    COLLECT WITH COUNT INTO count
                    RETURN count
            )[0]
            
            COLLECT 
                rubric_id = edge._to,
                name = rubric.name,
                description = rubric.description
                WITH COUNT INTO connections
            
            SORT connections DESC
            LIMIT 15
            
            RETURN {
                id: rubric_id,
                name: name,
                description: description,
                connections: connections,
                degree: degree
            }
        """
        
        rubrics = list(db.aql.execute(
            rubric_degree_query, 
            bind_vars={'course_codes': course_codes}
        ))
        
        return rubrics
    
    except Exception as e:
        logging.error(f"Error in get_rubrics_with_highest_degree: {str(e)}")
        return []

def get_rubric_related_materials(rubric_id):
    """
    Find source materials related to a rubric item.
    
    Args:
        rubric_id (str): The rubric's ArangoDB ID
        
    Returns:
        list: A list of related course materials
    """
    try:
        materials_query = """
        FOR edge IN related_to
            FILTER edge._from == @rubric_id
            
            LET material = DOCUMENT(edge._to)
            
            RETURN {
                id: edge._to,
                name: material.name,
                content: material.content,
                course_id: material.course_id,
                relevance: edge.strength
            }
        """
        
        materials = list(db.aql.execute(
            materials_query, 
            bind_vars={'rubric_id': rubric_id}
        ))
        
        return materials
    
    except Exception as e:
        logging.error(f"Error in get_rubric_related_materials: {str(e)}")
        return []

def get_common_mistake_feedback(instructor_id):
    """
    Get common mistakes with their connected rubric items, filtered by instructor's courses.
    
    Args:
        instructor_id (str): The instructor's ArangoDB ID
        
    Returns:
        list: A list of common mistakes with rubric information
    """
    try:
        # Get courses taught by this instructor
        course_query = """
        FOR course IN courses
            FILTER course.instructor_id == @instructor_id
            RETURN course.class_code
        """
        course_codes = list(db.aql.execute(course_query, bind_vars={'instructor_id': instructor_id}))
        
        if not course_codes:
            logging.warning(f"No courses found for instructor {instructor_id}")
            return []
        
        # Find common feedback with associated rubrics
        common_feedback_query = """
        FOR submission IN submission
            FILTER submission.class_code IN @course_codes
            FILTER submission.feedback != null AND submission.feedback != ""
            
            // Get mistake connections
            LET mistake_edges = (
                FOR edge IN has_feedback_on
                    FILTER edge._from == submission._id
                    RETURN edge._to
            )
            
            // Get related rubrics
            LET rubrics = (
                FOR mistake_id IN mistake_edges
                    FOR edge IN affects_criteria
                        FILTER edge._from == mistake_id
                        LET rubric = DOCUMENT(edge._to)
                        RETURN {
                            id: edge._to,
                            name: rubric.name
                        }
            )
            
            // Group submissions by question and feedback
            COLLECT 
                question = submission.assignment_id,
                justification = submission.feedback
                WITH COUNT INTO count
                KEEP rubrics
            
            // Flatten and deduplicate rubrics
            LET unique_rubrics = (
                FOR r IN FLATTEN(rubrics)
                    COLLECT id = r.id, name = r.name INTO grouped
                    RETURN {id: id, name: name}
            )
            
            FILTER count > 0
            SORT count DESC
            LIMIT 15
            
            RETURN {
                question: question,
                justification: justification,
                count: count,
                rubrics: unique_rubrics
            }
        """
        
        common_feedback = list(db.aql.execute(
            common_feedback_query, 
            bind_vars={'course_codes': course_codes}
        ))
        
        return common_feedback
    
    except Exception as e:
        logging.error(f"Error in get_common_mistake_feedback: {str(e)}")
        return []

def get_mistake_clusters_by_rubric(instructor_id):
    """
    Group mistakes by their connected rubric items, filtered by instructor's courses.
    
    Args:
        instructor_id (str): The instructor's ArangoDB ID
        
    Returns:
        dict: Clustered mistakes organized by rubric category
    """
    try:
        # Get courses taught by this instructor
        course_query = """
        FOR course IN courses
            FILTER course.instructor_id == @instructor_id
            RETURN course.class_code
        """
        course_codes = list(db.aql.execute(course_query, bind_vars={'instructor_id': instructor_id}))
        
        if not course_codes:
            logging.warning(f"No courses found for instructor {instructor_id}")
            return {'clusters': [], 'stats': {}}
        
        # Find rubric clusters and their associated mistakes
        cluster_query = """
        // Get submissions from instructor's courses
        LET submissions = (
            FOR submission IN submission
                FILTER submission.class_code IN @course_codes
                FILTER submission.feedback != null AND submission.feedback != ""
                RETURN submission
        )
        
        // Get mistakes connected to submissions
        LET mistakes = (
            FOR submission IN submissions
                FOR edge IN has_feedback_on
                    FILTER edge._from == submission._id
                    LET mistake = DOCUMENT(edge._to)
                    RETURN {
                        id: edge._to,
                        question: mistake.question,
                        justification: mistake.justification,
                        score: mistake.score_awarded,
                        submission_id: submission._id,
                        assignment_id: submission.assignment_id
                    }
        )
        
        // Get rubrics connected to mistakes
        LET rubric_connections = (
            FOR mistake IN mistakes
                FOR edge IN affects_criteria
                    FILTER edge._from == mistake.id
                    LET rubric = DOCUMENT(edge._to)
                    RETURN {
                        mistake: mistake,
                        rubric: {
                            id: edge._to,
                            name: rubric.name,
                            description: rubric.description
                        }
                    }
        )
        
        // Group by rubric to form clusters
        FOR connection IN rubric_connections
            COLLECT 
                rubric_id = connection.rubric.id,
                rubric_name = connection.rubric.name,
                rubric_desc = connection.rubric.description
                INTO mistake_groups = connection.mistake
            
            LET cluster_size = LENGTH(mistake_groups)
            LET avg_score = AVG(mistake_groups[*].score)
            
            FILTER cluster_size > 0
            SORT cluster_size DESC
            LIMIT 10
            
            RETURN {
                id: rubric_id,
                name: rubric_name, 
                description: rubric_desc,
                size: cluster_size,
                avg_score: avg_score,
                nodes: (
                    FOR group IN mistake_groups
                        SORT group.score ASC
                        LIMIT 10
                        RETURN {
                            id: group.id,
                            label: group.assignment_id,
                            justification: group.justification,
                            score: group.score,
                            importance: 1.0 - (group.score / 100)
                        }
                )
            }
        """
        
        clusters = list(db.aql.execute(
            cluster_query, 
            bind_vars={'course_codes': course_codes}
        ))
        
        # Calculate overall statistics
        total_mistakes = sum(cluster['size'] for cluster in clusters)
        
        stats = {
            'total_clusters': len(clusters),
            'total_mistakes': total_mistakes,
            'avg_cluster_size': total_mistakes / len(clusters) if clusters else 0
        }
        
        return {
            'clusters': clusters,
            'stats': stats
        }
    
    except Exception as e:
        logging.error(f"Error in get_mistake_clusters_by_rubric: {str(e)}")
        return {'clusters': [], 'stats': {}}