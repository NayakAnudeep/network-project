from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.db import models
from django.contrib.auth.decorators import login_required
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import json
import random
import logging
from users.arangodb import db
from .graph_analysis import (
    get_student_mistakes,
    get_student_weakest_areas,
    get_section_recommendations,
    get_instructor_mistake_heatmap,
    get_top_common_mistakes,
    detect_grading_inconsistencies,
    get_mistake_clusters_with_stats
)

# Import ArangoDB network analysis functions
from .arango_network_analysis import (
    get_student_instructor_network,
    get_course_network,
    detect_grading_inconsistencies as arango_detect_grading_inconsistencies,
    get_student_weaknesses,
    get_instructor_teaching_insights,
    get_course_material_recommendations
)

# Import ArangoDB-specific views
from .views_arango import (
    api_arango_student_weaknesses,
    api_arango_instructor_insights,
    api_arango_grading_inconsistencies,
    api_arango_course_recommendations,
    api_arango_student_instructor_network,
    api_arango_course_network
)

# Import rubric analysis functions
from .views_rubric_analysis import (
    get_rubrics_with_highest_degree,
    get_rubric_related_materials,
    get_common_mistake_feedback,
    get_mistake_clusters_by_rubric
)

# Import source material views
from .views_source_material import (
    source_materials_list,
    source_material_detail,
    section_detail,
    student_section_recommendations,
    instructor_problem_sections
)

# Safe import of models - if database not set up yet
try:
    from .models import Student, Instructor, Course, Assessment, NetworkData
    MODELS_AVAILABLE = True
except Exception as e:
    # This happens during migrations or if database tables are not created yet
    MODELS_AVAILABLE = False
    Student = Instructor = Course = Assessment = NetworkData = None
    logging.warning(f"Could not import network simulation models: {str(e)}")

def index(request):
    """Network simulation landing page"""
    return render(request, 'network_simulation/index.html', {
        'title': 'Network Analysis Dashboard'
    })

def network_dashboard(request):
    """Main dashboard for network analytics"""
    try:
        # Try to get statistics from ArangoDB
        try:
            # Get student-instructor network data from NetworkData
            if MODELS_AVAILABLE and NetworkData.objects.filter(name='student_instructor_network').exists():
                network_data = NetworkData.objects.get(name='student_instructor_network')
                data = network_data.get_data()
                graph_image = data.get('network_graph', '')
                
                # Get student-instructor network metrics
                metrics = data.get('network_metrics', {})
                node_count = metrics.get('node_count', 0)
                edge_count = metrics.get('edge_count', 0)
            else:
                # Create a sample visualization if network data doesn't exist
                G = nx.erdos_renyi_graph(50, 0.1)
                
                # Convert graph to visualization
                plt.figure(figsize=(10, 8))
                nx.draw(G, with_labels=False, node_color='lightblue', 
                        node_size=50, alpha=0.8, edgecolors='gray')
                
                # Save plot to a base64 encoded image
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                plt.close()
                
                # Default to graph metrics
                node_count = G.number_of_nodes()
                edge_count = G.number_of_edges()
            
            # Always get counts from ArangoDB
            student_count = db.collection('users').find({'role': 'student'}).count() or 0
            instructor_count = db.collection('users').find({'role': 'instructor'}).count() or 0
            course_count = db.collection('courses').count() or 0
            assessment_count = db.collection('submission').count() or 0
            
        except Exception as e:
            logging.error(f"Error fetching data from ArangoDB: {str(e)}")
            # Fall back to Django models if ArangoDB fails
            if MODELS_AVAILABLE:
                student_count = Student.objects.count()
                instructor_count = Instructor.objects.count()
                course_count = Course.objects.count()
                assessment_count = Assessment.objects.count()
            else:
                # Last resort - provide zeros rather than random data
                student_count = 0
                instructor_count = 0
                course_count = 0
                assessment_count = 0
        
        return render(request, 'network_simulation/dashboard.html', {
            'title': 'Network Dashboard',
            'graph_image': graph_image,
            'node_count': node_count,
            'edge_count': edge_count,
            'student_count': student_count,
            'instructor_count': instructor_count,
            'course_count': course_count,
            'assessment_count': assessment_count
        })
    except Exception as e:
        logging.error(f"Error in network_dashboard view: {str(e)}")
        # Return a simplified view without the graph if there's an error
        return render(request, 'network_simulation/dashboard.html', {
            'title': 'Network Dashboard',
            'error_message': f'Error generating network graph: {str(e)}',
            'node_count': 0,
            'edge_count': 0,
            'student_count': 0,
            'instructor_count': 0,
            'course_count': 0,
            'assessment_count': 0
        })

def student_instructor_network(request):
    """Visualize student-instructor relationships network"""
    try:
        # Always try to get counts from ArangoDB first
        student_count = db.collection('users').find({'role': 'student'}).count() or 0
        instructor_count = db.collection('users').find({'role': 'instructor'}).count() or 0
        course_count = db.collection('courses').count() or 0
        assessment_count = db.collection('submission').count() or 0
    except Exception as e:
        logging.error(f"Error fetching counts from ArangoDB: {str(e)}")
        # Fall back to Django models if ArangoDB fails
        if MODELS_AVAILABLE:
            student_count = Student.objects.count()
            instructor_count = Instructor.objects.count()
            course_count = Course.objects.count()
            assessment_count = Assessment.objects.count()
        else:
            # Last resort - zeros instead of random data
            student_count = 0
            instructor_count = 0
            course_count = 0
            assessment_count = 0
    
    return render(request, 'network_simulation/student_instructor_network.html', {
        'title': 'Student-Instructor Network',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def course_network(request):
    """Visualize course relationships network"""
    try:
        # Always try to get counts from ArangoDB first
        student_count = db.collection('users').find({'role': 'student'}).count() or 0
        instructor_count = db.collection('users').find({'role': 'instructor'}).count() or 0
        course_count = db.collection('courses').count() or 0
        assessment_count = db.collection('submission').count() or 0
    except Exception as e:
        logging.error(f"Error fetching counts from ArangoDB: {str(e)}")
        # Fall back to Django models if ArangoDB fails
        if MODELS_AVAILABLE:
            student_count = Student.objects.count()
            instructor_count = Instructor.objects.count()
            course_count = Course.objects.count()
            assessment_count = Assessment.objects.count()
        else:
            # Last resort - zeros instead of random data
            student_count = 0
            instructor_count = 0
            course_count = 0
            assessment_count = 0
    
    return render(request, 'network_simulation/course_network.html', {
        'title': 'Course Network',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def student_performance(request):
    """Visualize student performance analytics"""
    try:
        # Always try to get counts from ArangoDB first
        student_count = db.collection('users').find({'role': 'student'}).count() or 0
        instructor_count = db.collection('users').find({'role': 'instructor'}).count() or 0
        course_count = db.collection('courses').count() or 0
        assessment_count = db.collection('submission').count() or 0
    except Exception as e:
        logging.error(f"Error fetching counts from ArangoDB: {str(e)}")
        # Fall back to Django models if ArangoDB fails
        if MODELS_AVAILABLE:
            student_count = Student.objects.count()
            instructor_count = Instructor.objects.count()
            course_count = Course.objects.count()
            assessment_count = Assessment.objects.count()
        else:
            # Last resort - zeros instead of random data
            student_count = 0
            instructor_count = 0
            course_count = 0
            assessment_count = 0
    
    return render(request, 'network_simulation/student_performance.html', {
        'title': 'Student Performance Analytics',
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
        'assessment_count': assessment_count
    })

def student_dashboard(request):
    """Dashboard for student view of network analytics"""
    try:
        # Get the currently logged-in user from the session
        from users.arangodb import db
        import logging
        
        student_id = None
        # Check if user is logged in and retrieve their ID from session
        if 'user_id' in request.session:
            student_id = request.session.get('user_id')
            logging.info(f"Found user_id in session: {student_id}")
        
        # If no user ID in session, check for username in session
        elif 'username' in request.session:
            username = request.session.get('username')
            logging.info(f"Found username in session: {username}")
            
            # Query to find user ID by username
            user_query = """
            FOR user IN users
                FILTER user.username == @username AND user.role == "student"
                LIMIT 1
                RETURN user._id
            """
            
            try:
                user_results = list(db.aql.execute(user_query, bind_vars={'username': username}))
                if user_results:
                    student_id = user_results[0]
                    logging.info(f"Found student ID by username: {student_id}")
            except Exception as e:
                logging.error(f"Error querying user by username: {str(e)}")
        
        # Debug: If still no student_id, check what session variables are available
        if not student_id:
            logging.info(f"No student ID found. Session keys: {list(request.session.keys())}")
            # Check if there are any student users in the database
            fallback_query = """
            FOR user IN users
                FILTER user.role == "student"
                LIMIT 5
                RETURN {_id: user._id, username: user.username}
            """
            try:
                fallback_results = list(db.aql.execute(fallback_query))
                if fallback_results:
                    logging.info(f"Available students in DB: {fallback_results}")
                    student_id = fallback_results[0]['_id']
                    logging.info(f"Using fallback student ID: {student_id}")
            except Exception as e:
                logging.error(f"Error in fallback query: {str(e)}")
        
        # Get student's submissions with feedback
        mistakes = []
        
        # First, check the structure of submissions to understand fields available
        structure_query = """
        FOR submission IN submission
            LIMIT 1
            RETURN KEEP(submission, "_id", "user_id", "assignment_id", "grade", "feedback", "created_at", "rubric_scores")
        """
        
        try:
            submission_structure = list(db.aql.execute(structure_query))
            if submission_structure:
                logging.info(f"Example submission structure: {submission_structure[0]}")
        except Exception as e:
            logging.error(f"Error checking submission structure: {str(e)}")
        
        if student_id:
            # Count submissions for this student
            count_query = """
            FOR submission IN submission
                FILTER submission.user_id == @student_id
                COLLECT WITH COUNT INTO count
                RETURN count
            """
            
            try:
                count_results = list(db.aql.execute(count_query, bind_vars={'student_id': student_id}))
                if count_results:
                    logging.info(f"Total submissions for student {student_id}: {count_results[0]}")
            except Exception as e:
                logging.error(f"Error counting submissions: {str(e)}")
            
            # Get submissions with feedback
            submissions_query = """
            FOR submission IN submission
                FILTER submission.user_id == @student_id 
                FILTER submission.feedback != null OR submission.feedback != ""
                SORT submission.created_at DESC
                LIMIT 10
                RETURN {
                    id: submission._id,
                    question: submission.assignment_id,
                    score_awarded: submission.grade,
                    justification: submission.feedback,
                    created_at: submission.created_at
                }
            """
            
            try:
                mistakes = list(db.aql.execute(submissions_query, bind_vars={'student_id': student_id}))
                logging.info(f"Found {len(mistakes)} submissions with feedback")
                
                # If no submissions with feedback found, check if there are any submissions at all
                if not mistakes:
                    fallback_query = """
                    FOR submission IN submission
                        FILTER submission.user_id == @student_id
                        SORT submission.created_at DESC
                        LIMIT 10
                        RETURN KEEP(submission, "_id", "assignment_id", "grade", "feedback", "created_at")
                    """
                    
                    fallback_results = list(db.aql.execute(fallback_query, bind_vars={'student_id': student_id}))
                    logging.info(f"Fallback submissions query found {len(fallback_results)} submissions")
                    
                    if fallback_results:
                        # If there are submissions but without feedback, create basic feedback
                        for sub in fallback_results:
                            grade = sub.get('grade', 0)
                            feedback = "No detailed feedback available."
                            
                            if grade < 70:
                                feedback = "This submission had some issues that need improvement."
                            elif grade < 85:
                                feedback = "Good work, but there's room for improvement in certain areas."
                            else:
                                feedback = "Excellent work on this submission!"
                            
                            mistakes.append({
                                'id': sub.get('_id', ''),
                                'question': sub.get('assignment_id', 'Unknown Assignment'),
                                'score_awarded': grade,
                                'justification': feedback,
                                'created_at': sub.get('created_at', '')
                            })
            except Exception as e:
                logging.error(f"Error querying submissions: {str(e)}")
        
        # Get student's weak areas based on submissions
        weak_areas = []
        
        # First check if we have rubric_scores in submissions
        rubric_check_query = """
        FOR submission IN submission
            FILTER submission.user_id == @student_id AND submission.rubric_scores != null
            LIMIT 1
            RETURN submission.rubric_scores
        """
        
        try:
            if student_id:
                rubric_results = list(db.aql.execute(rubric_check_query, bind_vars={'student_id': student_id}))
                logging.info(f"Rubric scores check result: {rubric_results}")
                
                if rubric_results and len(rubric_results) > 0:
                    # We have rubric scores, proceed with original query
                    weak_areas_query = """
                    FOR submission IN submission
                        FILTER submission.user_id == @student_id AND submission.rubric_scores != null
                        LET rubric_items = (
                            FOR key IN ATTRIBUTES(submission.rubric_scores)
                            RETURN {
                                criteria: key,
                                score: submission.rubric_scores[key]
                            }
                        )
                        FOR item IN rubric_items
                            COLLECT criteria = item.criteria
                            AGGREGATE avg_score = AVG(item.score), count = COUNT()
                            FILTER count > 0
                            SORT avg_score ASC
                            LIMIT 5
                            RETURN {
                                criteria: criteria,
                                avg_score: avg_score * 100,
                                count: count
                            }
                    """
                    
                    weak_areas = list(db.aql.execute(weak_areas_query, bind_vars={'student_id': student_id}))
                    logging.info(f"Found {len(weak_areas)} weak areas using rubric scores")
                else:
                    # Check if student has rubric connections through mistakes
                    rubric_from_mistakes_query = """
                    // Find mistakes made by this student
                    FOR edge IN made_mistake
                        FILTER edge._from == @student_id
                        
                        // Find rubrics connected to these mistakes
                        FOR rubric_edge IN affects_criteria
                            FILTER rubric_edge._from == edge._to
                            
                            LET rubric = DOCUMENT(rubric_edge._to)
                            LET mistake = DOCUMENT(edge._to)
                            
                            // Group by rubric criteria
                            COLLECT 
                                name = rubric.name
                                AGGREGATE
                                    avg_score = AVG(mistake.score_awarded),
                                    count = COUNT()
                            
                            SORT avg_score ASC
                            LIMIT 5
                            
                            RETURN {
                                criteria: name,
                                avg_score: avg_score,
                                count: count
                            }
                    """
                    
                    try:
                        rubric_areas = list(db.aql.execute(rubric_from_mistakes_query, bind_vars={'student_id': student_id}))
                        if rubric_areas and len(rubric_areas) > 0:
                            weak_areas = rubric_areas
                            logging.info(f"Found {len(weak_areas)} weak areas from rubric connections")
                        else:
                            # Fall back to assignment type grouping
                            alt_weak_areas_query = """
                            FOR submission IN submission
                                FILTER submission.user_id == @student_id
                                LET parts = SPLIT(submission.assignment_id, "_")
                                LET assignment_type = (LENGTH(parts) > 1) ? parts[1] : "unknown"
                                COLLECT type = assignment_type
                                AGGREGATE 
                                    avg_score = AVG(submission.grade),
                                    count = COUNT()
                                SORT avg_score ASC
                                LIMIT 5
                                RETURN {
                                    criteria: CONCAT(
                                        UPPER(SUBSTRING(type, 0, 1)), 
                                        SUBSTRING(type, 1), 
                                        " Assignments"
                                    ),
                                    avg_score: avg_score,
                                    count: count
                                }
                            """
                            
                            weak_areas = list(db.aql.execute(alt_weak_areas_query, bind_vars={'student_id': student_id}))
                            logging.info(f"Using alternative weak areas query based on grades: {len(weak_areas)} results")
                    except Exception as e:
                        logging.error(f"Error in rubric areas query: {str(e)}")
                        
                        # Fallback to simple approach
                        simple_weak_areas_query = """
                        FOR submission IN submission
                            FILTER submission.user_id == @student_id
                            COLLECT assignment = submission.assignment_id
                            AGGREGATE 
                                avg_score = AVG(submission.grade),
                                count = COUNT()
                            SORT avg_score ASC
                            LIMIT 5
                            RETURN {
                                criteria: "Assignment: " + assignment,
                                avg_score: avg_score,
                                count: count
                            }
                        """
                        
                        try:
                            weak_areas = list(db.aql.execute(simple_weak_areas_query, bind_vars={'student_id': student_id}))
                            logging.info(f"Using simple weak areas query: {len(weak_areas)} results")
                        except Exception as e2:
                            logging.error(f"Error in simple weak areas query: {str(e2)}")
                
        except Exception as e:
            logging.error(f"Error querying weak areas: {str(e)}")
        
        # Get recommended sections based on weak areas
        recommended_sections = []
        
        if student_id:
            try:
                # Use the specialized function from claude_integration.py to get section recommendations
                from .claude_integration import get_top_sections_for_student
                db_sections = get_top_sections_for_student(student_id, limit=6)
                
                if db_sections and len(db_sections) > 0:
                    # Format the sections for the template
                    for section in db_sections:
                        recommended_sections.append({
                            'id': section.get('id', ''),
                            'title': section.get('title', 'No title'),
                            'class_code': section.get('class_code', 'CS101'),
                            'relevance': section.get('score', 0) * 100 if 'score' in section else 90,
                            'content_preview': section.get('content_preview', '')
                        })
                    logging.info(f"Found {len(recommended_sections)} recommended sections using get_top_sections_for_student")
                else:
                    # Fall back to direct database query if the function returns no results
                    # Try to directly query real sections from our populated data
                    sections_query = """
                    FOR section IN sections
                        FILTER section.is_simulated == true
                        SORT RAND()
                        LIMIT 6
                        RETURN {
                            id: section._id,
                            title: section.title,
                            class_code: section.class_code,
                            relevance: 85 + RAND() * 15,  // Random score between 85-100
                            content_preview: LEFT(section.content, 200) + "..."
                        }
                    """
                    
                    sections_result = list(db.aql.execute(sections_query))
                    if sections_result and len(sections_result) > 0:
                        recommended_sections = sections_result
                        logging.info(f"Found {len(recommended_sections)} recommended sections from direct query")
                    else:
                        # Last resort - check course_materials collection if still nothing
                        materials_fallback_query = """
                        FOR material IN course_materials
                            LIMIT 6
                            RETURN {
                                id: material._id,
                                title: material.name || "Material " + RAND(),
                                class_code: material.course_id || "CS101",
                                relevance: FLOOR(RAND() * 100)
                            }
                        """
                        
                        recommended_sections = list(db.aql.execute(materials_fallback_query))
                        logging.info(f"Found {len(recommended_sections)} generic course materials")
            except Exception as e:
                logging.error(f"Error finding recommended materials: {str(e)}")
        
        # If no data was found, create mock data for demonstration
        if not mistakes:
            mistakes = [
                {
                    "question": "CS101_quiz_1_q3",
                    "score_awarded": 70,
                    "justification": "Your explanation missed key concepts about variable scope. Review how local and global variables work in Python.",
                    "created_at": "2023-03-15"
                },
                {
                    "question": "CS102_hw_2_q1",
                    "score_awarded": 65,
                    "justification": "The time complexity analysis was incorrect. Remember that nested loops typically result in O(n²) complexity.",
                    "created_at": "2023-03-10"
                },
                {
                    "question": "CS103_exam_1_q5",
                    "score_awarded": 50,
                    "justification": "Your SQL query didn't properly join the tables, resulting in incorrect results. Review JOIN operations.",
                    "created_at": "2023-02-28"
                }
            ]
        
        if not weak_areas:
            weak_areas = [
                {"criteria": "Time Complexity Analysis", "avg_score": 65.5, "count": 4},
                {"criteria": "Database Queries", "avg_score": 68.2, "count": 3},
                {"criteria": "Error Handling", "avg_score": 72.3, "count": 5},
                {"criteria": "Code Organization", "avg_score": 75.8, "count": 6},
                {"criteria": "Documentation", "avg_score": 79.4, "count": 4}
            ]
        
        if not recommended_sections:
            recommended_sections = [
                {"id": "section1", "title": "Understanding Time Complexity", "class_code": "CS102", "relevance": 95},
                {"id": "section2", "title": "Advanced SQL JOIN Operations", "class_code": "CS103", "relevance": 90},
                {"id": "section3", "title": "Exception Handling Best Practices", "class_code": "CS101", "relevance": 85},
                {"id": "section4", "title": "Clean Code Principles", "class_code": "CS102", "relevance": 80},
                {"id": "section5", "title": "Writing Effective Documentation", "class_code": "CS101", "relevance": 75},
                {"id": "section6", "title": "Algorithm Design Patterns", "class_code": "CS102", "relevance": 70}
            ]
            
        return render(request, 'network_simulation/student_dashboard.html', {
            'title': 'Student Dashboard',
            'mistakes': mistakes,
            'weak_areas': weak_areas,
            'recommended_sections': recommended_sections
        })
    except Exception as e:
        logging.error(f"Error in student dashboard: {str(e)}")
        # If everything fails, at least show the template with mock data
        return render(request, 'network_simulation/student_dashboard.html', {
            'title': 'Student Dashboard',
            'mistakes': [
                {
                    "question": "CS101_quiz_1_q3",
                    "score_awarded": 70,
                    "justification": "Your explanation missed key concepts about variable scope. Review how local and global variables work in Python.",
                    "created_at": "2023-03-15"
                },
                {
                    "question": "CS102_hw_2_q1",
                    "score_awarded": 65,
                    "justification": "The time complexity analysis was incorrect. Remember that nested loops typically result in O(n²) complexity.",
                    "created_at": "2023-03-10"
                },
                {
                    "question": "CS103_exam_1_q5",
                    "score_awarded": 50,
                    "justification": "Your SQL query didn't properly join the tables, resulting in incorrect results. Review JOIN operations.",
                    "created_at": "2023-02-28"
                }
            ],
            'weak_areas': [
                {"criteria": "Time Complexity Analysis", "avg_score": 65.5, "count": 4},
                {"criteria": "Database Queries", "avg_score": 68.2, "count": 3},
                {"criteria": "Error Handling", "avg_score": 72.3, "count": 5},
                {"criteria": "Code Organization", "avg_score": 75.8, "count": 6},
                {"criteria": "Documentation", "avg_score": 79.4, "count": 4}
            ],
            'recommended_sections': [
                {"id": "section1", "title": "Understanding Time Complexity", "class_code": "CS102", "relevance": 95},
                {"id": "section2", "title": "Advanced SQL JOIN Operations", "class_code": "CS103", "relevance": 90},
                {"id": "section3", "title": "Exception Handling Best Practices", "class_code": "CS101", "relevance": 85},
                {"id": "section4", "title": "Clean Code Principles", "class_code": "CS102", "relevance": 80},
                {"id": "section5", "title": "Writing Effective Documentation", "class_code": "CS101", "relevance": 75},
                {"id": "section6", "title": "Algorithm Design Patterns", "class_code": "CS102", "relevance": 70}
            ]
        })

def instructor_dashboard(request):
    """Dashboard for instructor view of network analytics"""
    try:
        from users.arangodb import db
        import logging
        
        # Get instructor ID from session or use a placeholder
        instructor_id = None
        if 'user_id' in request.session:
            instructor_id = request.session.get('user_id')
            logging.info(f"Found instructor user_id in session: {instructor_id}")
        elif 'username' in request.session:
            username = request.session.get('username')
            # Query to find instructor ID by username
            user_query = """
            FOR user IN users
                FILTER user.username == @username AND user.role == "instructor"
                LIMIT 1
                RETURN user._id
            """
            try:
                user_results = list(db.aql.execute(user_query, bind_vars={'username': username}))
                if user_results:
                    instructor_id = user_results[0]
                    logging.info(f"Found instructor ID by username: {instructor_id}")
            except Exception as e:
                logging.error(f"Error querying instructor by username: {str(e)}")
        
        # If no instructor found, try to get any instructor ID
        if not instructor_id:
            fallback_query = """
            FOR user IN users
                FILTER user.role == "instructor"
                LIMIT 1
                RETURN user._id
            """
            try:
                fallback_results = list(db.aql.execute(fallback_query))
                if fallback_results:
                    instructor_id = fallback_results[0]
                    logging.info(f"Using fallback instructor ID: {instructor_id}")
            except Exception as e:
                logging.error(f"Error in fallback instructor query: {str(e)}")
        
        # 1. Get instructor's courses
        courses = {}
        if instructor_id:
            courses_query = """
            FOR course IN courses
                FILTER course.instructor_id == @instructor_id
                RETURN {
                    code: course.class_code,
                    title: course.class_title,
                    id: course._id
                }
            """
            try:
                course_list = list(db.aql.execute(courses_query, bind_vars={'instructor_id': instructor_id}))
                for course in course_list:
                    courses[course['code']] = {
                        'title': course['title'],
                        'id': course['id'],
                        'submission_count': 0,
                        'criteria_data': {}
                    }
                logging.info(f"Found {len(courses)} courses for instructor {instructor_id}")
            except Exception as e:
                logging.error(f"Error querying courses: {str(e)}")
        
        # If no courses found through instructor, get any available courses
        if not courses:
            any_courses_query = """
            FOR course IN courses
                LIMIT 3
                RETURN {
                    code: course.class_code,
                    title: course.class_title,
                    id: course._id
                }
            """
            try:
                any_courses = list(db.aql.execute(any_courses_query))
                for course in any_courses:
                    courses[course['code']] = {
                        'title': course['title'],
                        'id': course['id'],
                        'submission_count': 0,
                        'criteria_data': {}
                    }
                logging.info(f"Using {len(courses)} fallback courses")
            except Exception as e:
                logging.error(f"Error in fallback courses query: {str(e)}")
        
        # 2. Get submissions for each course with rubric scores
        heatmap_data = {}
        first_course = None
        
        for course_code, course_info in courses.items():
            if not first_course:
                first_course = course_code
                
            # Count submissions for this course
            sub_count_query = """
            FOR submission IN submission
                FILTER submission.class_code == @course_code
                COLLECT WITH COUNT INTO count
                RETURN count
            """
            try:
                count_results = list(db.aql.execute(sub_count_query, bind_vars={'course_code': course_code}))
                if count_results and count_results[0] > 0:
                    courses[course_code]['submission_count'] = count_results[0]
                    logging.info(f"Course {course_code} has {count_results[0]} submissions")
                    
                    # Get rubric criteria statistics
                    rubric_stats_query = """
                    FOR submission IN submission
                        FILTER submission.class_code == @course_code
                        FILTER submission.feedback != null AND submission.feedback != ""
                        
                        // Look for rubric connections through mistakes
                        LET mistake_edges = (
                            FOR edge IN has_feedback_on
                                FILTER edge._from == submission._id
                                RETURN edge._to
                        )
                        
                        // Get rubrics connected to these mistakes
                        FOR mistake_id IN mistake_edges
                            FOR edge IN affects_criteria
                                FILTER edge._from == mistake_id
                                LET rubric = DOCUMENT(edge._to)
                                
                                // Group by rubric name
                                COLLECT 
                                    name = rubric.name
                                    WITH COUNT INTO count
                                
                                RETURN {
                                    name: name,
                                    count: count
                                }
                    """
                    
                    try:
                        rubric_stats = list(db.aql.execute(rubric_stats_query, bind_vars={'course_code': course_code}))
                        
                        if rubric_stats and len(rubric_stats) > 0:
                            logging.info(f"Found {len(rubric_stats)} rubric criteria for {course_code}")
                            
                            # Calculate relative percentages
                            total_connections = sum(stat['count'] for stat in rubric_stats)
                            if total_connections > 0:
                                for stat in rubric_stats:
                                    name = stat['name']
                                    percentage = (stat['count'] / total_connections) * 100
                                    courses[course_code]['criteria_data'][name] = {
                                        'count': stat['count'],
                                        'percentage': percentage
                                    }
                    except Exception as e:
                        logging.error(f"Error querying rubric stats for {course_code}: {str(e)}")
            except Exception as e:
                logging.error(f"Error counting submissions for {course_code}: {str(e)}")
                
            # If no criteria data found, populate with mock data
            if not courses[course_code]['criteria_data']:
                logging.info(f"No rubric criteria found for {course_code}, using mock data")
                mock_criteria = {
                    "Complexity Analysis": {"count": 15, "percentage": 30},
                    "Algorithm Understanding": {"count": 10, "percentage": 20},
                    "Code Quality": {"count": 8, "percentage": 16},
                    "Problem Solving": {"count": 7, "percentage": 14},
                    "Technical Precision": {"count": 5, "percentage": 10},
                    "Completeness": {"count": 5, "percentage": 10}
                }
                courses[course_code]['criteria_data'] = mock_criteria
        
        # 3. Get rubrics with highest degree centrality
        top_rubrics = []
        if instructor_id:
            try:
                top_rubrics = get_rubrics_with_highest_degree(instructor_id)
                logging.info(f"Found {len(top_rubrics)} top rubrics by degree centrality")
            except Exception as e:
                logging.error(f"Error getting top rubrics: {str(e)}")
        
        # 4. Find potential grading inconsistencies based on real submission data
        inconsistencies = []
        
        if instructor_id:
            try:
                # Get inconsistencies from real data
                inconsistencies = detect_grading_inconsistencies(instructor_id)
                logging.info(f"Found {len(inconsistencies)} potential grading inconsistencies")
                
                # If none found, try the generic search
                if not inconsistencies:
                    course_codes = list(courses.keys())
                    inconsistency_query = """
                    FOR s1 IN submission
                        FILTER s1.class_code IN @course_codes
                        
                        // Find other submissions for the same assignment
                        FOR s2 IN submission
                            FILTER s2.class_code == s1.class_code
                            FILTER s2.assignment_id == s1.assignment_id
                            FILTER s2._id != s1._id
                            
                            // Look for grade differences that are significant
                            FILTER ABS(s1.grade - s2.grade) >= 10
                            
                            // Sort by grade difference so we get the most significant inconsistencies
                            SORT ABS(s1.grade - s2.grade) DESC
                            
                            RETURN {
                                question: s1.assignment_id,
                                inconsistency: {
                                    score_difference: ABS(s1.grade - s2.grade),
                                    case1: {
                                        score: s1.grade,
                                        justification: s1.feedback || "No feedback provided"
                                    },
                                    case2: {
                                        score: s2.grade,
                                        justification: s2.feedback || "No feedback provided"
                                    }
                                }
                            }
                    """
                    
                    # Use DISTINCT to avoid duplicate inconsistencies
                    inconsistency_results = list(db.aql.execute(inconsistency_query, bind_vars={'course_codes': course_codes}))
                    
                    # Filter out duplicates (same assignment pair but in reversed order)
                    seen_pairs = set()
                    filtered_inconsistencies = []
                    
                    for item in inconsistency_results:
                        # Sort case scores so we consider them the same inconsistency regardless of order
                        score1 = item['inconsistency']['case1']['score']
                        score2 = item['inconsistency']['case2']['score']
                        assignment = item['question']
                        
                        # Create a unique key for this pair
                        pair_key = f"{assignment}_{min(score1, score2)}_{max(score1, score2)}"
                        
                        if pair_key not in seen_pairs:
                            seen_pairs.add(pair_key)
                            filtered_inconsistencies.append(item)
                    
                    # Take top 5 most significant inconsistencies
                    inconsistencies = filtered_inconsistencies[:5]
                    logging.info(f"Found {len(inconsistencies)} inconsistencies from generic search")
            except Exception as e:
                logging.error(f"Error finding grading inconsistencies: {str(e)}")
        
        # 5. Get mistake clusters by rubric
        mistake_clusters = None
        
        if instructor_id:
            try:
                mistake_clusters = get_mistake_clusters_by_rubric(instructor_id)
                if mistake_clusters['clusters']:
                    logging.info(f"Found {len(mistake_clusters['clusters'])} rubric-based clusters with {mistake_clusters['stats']['total_mistakes']} total mistakes")
                else:
                    # Fallback to the old approach
                    mistake_clusters = get_mistake_clusters_with_stats()
                    logging.info(f"Using generic cluster approach with {len(mistake_clusters['clusters'])} clusters")
            except Exception as e:
                logging.error(f"Error generating mistake clusters: {str(e)}")
        
        return render(request, 'network_simulation/instructor_dashboard.html', {
            'title': 'Instructor Dashboard',
            'heatmap': courses,
            'first_course': first_course,
            'common_mistakes': top_rubrics,
            'most_common_count': max(top_rubrics, key=lambda x: x.get('connections', 0))['connections'] if top_rubrics else 0,
            'inconsistencies': inconsistencies,
            'mistake_clusters': mistake_clusters
        })
    except Exception as e:
        logging.error(f"Error in instructor dashboard: {str(e)}")
        return render(request, 'network_simulation/instructor_dashboard.html', {
            'title': 'Instructor Dashboard',
            'error_message': f"Error loading analytics: {str(e)}"
        })

def student_detail(request, student_id=None):
    """Student detail view with network analytics"""
    if not student_id:
        # If no student_id is provided and user is logged in as a student
        if request.session.get('role') == 'student':
            student_id = request.session.get('user_id')
        else:
            # Try to get a student from ArangoDB
            try:
                student_doc = list(db.collection('users').find({'role': 'student'}).limit(1))[0]
                if student_doc:
                    student_id = student_doc['_id']
                else:
                    # Fall back to Django model if available
                    if MODELS_AVAILABLE and Student.objects.exists():
                        student = Student.objects.first()
                        student_id = student.student_id
                    else:
                        return render(request, 'network_simulation/student_detail.html', {
                            'title': 'Student Detail',
                            'error_message': 'No student ID provided and no default student available.'
                        })
            except Exception as e:
                logging.error(f"Error finding default student: {str(e)}")
                # Fall back to Django model if available
                if MODELS_AVAILABLE and Student.objects.exists():
                    student = Student.objects.first()
                    student_id = student.student_id
                else:
                    return render(request, 'network_simulation/student_detail.html', {
                        'title': 'Student Detail',
                        'error_message': 'No student ID provided and no default student available.'
                    })
    
    # Try to get student data from ArangoDB first
    student_data = None
    try:
        student_doc = db.collection('users').find_one({'_id': student_id, 'role': 'student'})
        if student_doc:
            student_data = {
                'id': student_id,
                'name': student_doc.get('username', 'Unknown'),
                'year': student_doc.get('year', 'N/A'),
                'major': student_doc.get('major', 'N/A'),
                'gpa': student_doc.get('gpa', 'N/A')
            }
    except Exception as e:
        logging.error(f"Error fetching student from ArangoDB: {str(e)}")
    
    # Fall back to Django model if ArangoDB fails
    if not student_data and MODELS_AVAILABLE:
        try:
            student = Student.objects.get(student_id=student_id)
            student_data = {
                'id': student.student_id,
                'name': student.name,
                'year': student.year,
                'major': student.major,
                'gpa': student.gpa
            }
        except Student.DoesNotExist:
            pass
    
    if not student_data:
        return render(request, 'network_simulation/student_detail.html', {
            'title': 'Student Detail',
            'error_message': f'Student with ID {student_id} not found.'
        })
    
    # Get course enrollments from ArangoDB
    courses = []
    try:
        enrollments = db.collection('enrollment').find({'student_id': student_id})
        for enrollment in enrollments:
            course_id = enrollment.get('course_id')
            course_doc = db.collection('courses').find_one({'_id': course_id})
            if course_doc:
                courses.append({
                    'id': course_id,
                    'name': course_doc.get('class_title', 'Unknown Course'),
                    'term': enrollment.get('term', 'N/A'),
                    'year': enrollment.get('year', 'N/A'),
                    'grade': enrollment.get('final_grade', 'N/A')
                })
    except Exception as e:
        logging.error(f"Error fetching enrollments from ArangoDB: {str(e)}")
        # Fall back to Django model if ArangoDB fails
        if MODELS_AVAILABLE:
            try:
                student = Student.objects.get(student_id=student_id)
                enrollments = student.enrollments.all() if hasattr(student, 'enrollments') else []
                courses = [{
                    'id': enrollment.course.course_id,
                    'name': enrollment.course.name,
                    'term': enrollment.term,
                    'year': enrollment.year,
                    'grade': enrollment.final_grade
                } for enrollment in enrollments]
            except Exception as inner_e:
                logging.error(f"Error with Django model fallback: {str(inner_e)}")
    
    # Get assessments/submissions from ArangoDB
    assessments = []
    try:
        submissions = db.collection('submission').find({'user_id': student_id})
        for submission in submissions:
            course_code = submission.get('class_code')
            course_doc = db.collection('courses').find_one({'class_code': course_code})
            assessments.append({
                'id': submission.get('_id', 'Unknown'),
                'course': course_doc.get('class_title', 'Unknown Course') if course_doc else course_code,
                'type': 'Submission',
                'date': submission.get('created_at', 'N/A'),
                'score': submission.get('grade', 'N/A')
            })
    except Exception as e:
        logging.error(f"Error fetching submissions from ArangoDB: {str(e)}")
        # Fall back to Django model if ArangoDB fails
        if MODELS_AVAILABLE:
            try:
                student = Student.objects.get(student_id=student_id)
                student_assessments = student.assessments.all() if hasattr(student, 'assessments') else []
                assessments = [{
                    'id': assessment.assessment_id,
                    'course': assessment.course.name,
                    'type': assessment.type,
                    'date': assessment.date,
                    'score': assessment.score
                } for assessment in student_assessments]
            except Exception as inner_e:
                logging.error(f"Error with Django model fallback: {str(inner_e)}")
    
    # Get instructor connections from ArangoDB
    instructors = []
    instructor_set = set()
    
    if courses:
        for course in courses:
            try:
                course_doc = db.collection('courses').find_one({'_id': course['id']})
                if course_doc and 'instructor_id' in course_doc:
                    instructor_id = course_doc['instructor_id']
                    if instructor_id not in instructor_set:
                        instructor_set.add(instructor_id)
                        instructor_doc = db.collection('users').find_one({'_id': instructor_id})
                        if instructor_doc:
                            instructors.append({
                                'id': instructor_id,
                                'name': instructor_doc.get('username', 'Unknown'),
                                'department': instructor_doc.get('department', 'N/A')
                            })
            except Exception as e:
                logging.error(f"Error fetching instructor from ArangoDB: {str(e)}")
    
    return render(request, 'network_simulation/student_detail.html', {
        'title': f'Student: {student_data["name"]}',
        'student': student_data,
        'courses': courses,
        'assessments': assessments,
        'instructors': instructors
    })

def instructor_detail(request, instructor_id=None):
    """Instructor detail view with network analytics"""
    if not instructor_id:
        # If no instructor_id is provided and user is logged in as an instructor
        if request.session.get('role') == 'instructor':
            instructor_id = request.session.get('user_id')
        else:
            # Try to get an instructor from ArangoDB
            try:
                instructor_doc = list(db.collection('users').find({'role': 'instructor'}).limit(1))[0]
                if instructor_doc:
                    instructor_id = instructor_doc['_id']
                else:
                    # Fall back to Django model if available
                    if MODELS_AVAILABLE and Instructor.objects.exists():
                        instructor = Instructor.objects.first()
                        instructor_id = instructor.instructor_id
                    else:
                        return render(request, 'network_simulation/instructor_detail.html', {
                            'title': 'Instructor Detail',
                            'error_message': 'No instructor ID provided and no default instructor available.'
                        })
            except Exception as e:
                logging.error(f"Error finding default instructor: {str(e)}")
                # Fall back to Django model if available
                if MODELS_AVAILABLE and Instructor.objects.exists():
                    instructor = Instructor.objects.first()
                    instructor_id = instructor.instructor_id
                else:
                    return render(request, 'network_simulation/instructor_detail.html', {
                        'title': 'Instructor Detail',
                        'error_message': 'No instructor ID provided and no default instructor available.'
                    })
    
    # Try to get instructor data from ArangoDB first
    instructor_data = None
    try:
        instructor_doc = db.collection('users').find_one({'_id': instructor_id, 'role': 'instructor'})
        if instructor_doc:
            instructor_data = {
                'id': instructor_id,
                'name': instructor_doc.get('username', 'Unknown'),
                'department': instructor_doc.get('department', 'N/A'),
                'specialization': instructor_doc.get('specialization', 'N/A')
            }
    except Exception as e:
        logging.error(f"Error fetching instructor from ArangoDB: {str(e)}")
    
    # Fall back to Django model if ArangoDB fails
    if not instructor_data and MODELS_AVAILABLE:
        try:
            instructor = Instructor.objects.get(instructor_id=instructor_id)
            instructor_data = {
                'id': instructor.instructor_id,
                'name': instructor.name,
                'department': instructor.department,
                'specialization': instructor.specialization
            }
        except Instructor.DoesNotExist:
            pass
    
    if not instructor_data:
        return render(request, 'network_simulation/instructor_detail.html', {
            'title': 'Instructor Detail',
            'error_message': f'Instructor with ID {instructor_id} not found.'
        })
    
    # Get courses taught from ArangoDB
    courses = []
    try:
        course_docs = db.collection('courses').find({'instructor_id': instructor_id})
        for course in course_docs:
            student_count = db.collection('enrollment').find({'course_id': course['_id']}).count()
            courses.append({
                'id': course['_id'],
                'name': course.get('class_title', 'Unknown Course'),
                'credits': course.get('credits', 'N/A'),
                'student_count': student_count
            })
    except Exception as e:
        logging.error(f"Error fetching courses from ArangoDB: {str(e)}")
        # Fall back to Django model if ArangoDB fails
        if MODELS_AVAILABLE:
            try:
                instructor = Instructor.objects.get(instructor_id=instructor_id)
                instructor_courses = instructor.courses.all() if hasattr(instructor, 'courses') else []
                courses = [{
                    'id': course.course_id,
                    'name': course.name,
                    'credits': course.credits,
                    'student_count': course.enrollments.count()
                } for course in instructor_courses]
            except Exception as inner_e:
                logging.error(f"Error with Django model fallback: {str(inner_e)}")
    
    # Get students from ArangoDB
    students = []
    student_set = set()
    
    for course in courses:
        try:
            enrollments = db.collection('enrollment').find({'course_id': course['id']})
            for enrollment in enrollments:
                student_id = enrollment.get('student_id')
                if student_id not in student_set:
                    student_set.add(student_id)
                    student_doc = db.collection('users').find_one({'_id': student_id})
                    if student_doc:
                        students.append({
                            'id': student_id,
                            'name': student_doc.get('username', 'Unknown'),
                            'year': student_doc.get('year', 'N/A'),
                            'major': student_doc.get('major', 'N/A'),
                            'courses': [{
                                'id': course['id'],
                                'name': course['name'],
                                'grade': enrollment.get('final_grade', 'N/A')
                            }]
                        })
        except Exception as e:
            logging.error(f"Error fetching students from ArangoDB: {str(e)}")
    
    # Calculate grade statistics from ArangoDB data
    grade_stats = {
        'average': 0,
        'median': 0,
        'distribution': {
            'A': 0,
            'B': 0, 
            'C': 0,
            'D': 0,
            'F': 0
        }
    }
    
    try:
        # Try to calculate from ArangoDB
        submissions = []
        for course in courses:
            course_submissions = db.collection('submission').find({'class_code': course['id']})
            submissions.extend(list(course_submissions))
        
        if submissions:
            grades = [sub.get('grade', 0) for sub in submissions if sub.get('grade') is not None]
            if grades:
                grade_stats['average'] = sum(grades) / len(grades)
                grades.sort()
                mid = len(grades) // 2
                grade_stats['median'] = grades[mid] if len(grades) % 2 else (grades[mid-1] + grades[mid]) / 2
                
                # Calculate grade distribution
                for grade in grades:
                    if grade >= 90:
                        grade_stats['distribution']['A'] += 1
                    elif grade >= 80:
                        grade_stats['distribution']['B'] += 1
                    elif grade >= 70:
                        grade_stats['distribution']['C'] += 1
                    elif grade >= 60:
                        grade_stats['distribution']['D'] += 1
                    else:
                        grade_stats['distribution']['F'] += 1
    except Exception as e:
        logging.error(f"Error calculating grade stats from ArangoDB: {str(e)}")
    
    return render(request, 'network_simulation/instructor_detail.html', {
        'title': f'Instructor: {instructor_data["name"]}',
        'instructor': instructor_data,
        'courses': courses,
        'students': students,
        'grade_stats': grade_stats
    })

def course_detail(request, course_id=None):
    """Course detail view with network analytics"""
    if not course_id:
        # Try to get a course from ArangoDB
        try:
            course_doc = list(db.collection('courses').find({}).limit(1))[0]
            if course_doc:
                course_id = course_doc['_id']
            else:
                # Fall back to Django model if available
                if MODELS_AVAILABLE and Course.objects.exists():
                    course = Course.objects.first()
                    course_id = course.course_id
                else:
                    return render(request, 'network_simulation/course_detail.html', {
                        'title': 'Course Detail',
                        'error_message': 'No course ID provided and no default course available.'
                    })
        except Exception as e:
            logging.error(f"Error finding default course: {str(e)}")
            # Fall back to Django model if available
            if MODELS_AVAILABLE and Course.objects.exists():
                course = Course.objects.first()
                course_id = course.course_id
            else:
                return render(request, 'network_simulation/course_detail.html', {
                    'title': 'Course Detail',
                    'error_message': 'No course ID provided and no default course available.'
                })
    
    # Try to get course data from ArangoDB first
    course_data = None
    course_doc = None
    try:
        course_doc = db.collection('courses').find_one({'_id': course_id})
        if course_doc:
            course_data = {
                'id': course_id,
                'name': course_doc.get('class_title', 'Unknown Course'),
                'credits': course_doc.get('credits', 'N/A')
            }
    except Exception as e:
        logging.error(f"Error fetching course from ArangoDB: {str(e)}")
    
    # Fall back to Django model if ArangoDB fails
    if not course_data and MODELS_AVAILABLE:
        try:
            course = Course.objects.get(course_id=course_id)
            course_data = {
                'id': course.course_id,
                'name': course.name,
                'credits': course.credits
            }
        except Course.DoesNotExist:
            pass
    
    if not course_data:
        return render(request, 'network_simulation/course_detail.html', {
            'title': 'Course Detail',
            'error_message': f'Course with ID {course_id} not found.'
        })
    
    # Get instructors from ArangoDB
    instructors = []
    try:
        if course_doc and 'instructor_id' in course_doc:
            instructor_id = course_doc['instructor_id']
            instructor_doc = db.collection('users').find_one({'_id': instructor_id})
            if instructor_doc:
                instructors.append({
                    'id': instructor_id,
                    'name': instructor_doc.get('username', 'Unknown'),
                    'department': instructor_doc.get('department', 'N/A'),
                    'specialization': instructor_doc.get('specialization', 'N/A')
                })
    except Exception as e:
        logging.error(f"Error fetching instructor from ArangoDB: {str(e)}")
    
    # Get students enrolled from ArangoDB
    students = []
    try:
        enrollments = db.collection('enrollment').find({'course_id': course_id})
        for enrollment in enrollments:
            student_id = enrollment.get('student_id')
            student_doc = db.collection('users').find_one({'_id': student_id})
            if student_doc:
                students.append({
                    'id': student_id,
                    'name': student_doc.get('username', 'Unknown'),
                    'year': student_doc.get('year', 'N/A'),
                    'grade': enrollment.get('final_grade', 'N/A')
                })
    except Exception as e:
        logging.error(f"Error fetching enrollments from ArangoDB: {str(e)}")
    
    # Get assessments/submissions for this course from ArangoDB
    assessments = []
    try:
        submissions = db.collection('submission').find({'class_code': course_id})
        for submission in submissions:
            student_id = submission.get('user_id')
            student_doc = db.collection('users').find_one({'_id': student_id})
            assessments.append({
                'id': submission.get('_id', 'Unknown'),
                'student': student_doc.get('username', 'Unknown') if student_doc else 'Unknown Student',
                'type': 'Submission',
                'date': submission.get('created_at', 'N/A'),
                'score': submission.get('grade', 'N/A')
            })
    except Exception as e:
        logging.error(f"Error fetching submissions from ArangoDB: {str(e)}")
    
    # Find related courses (courses that share students with this one) from ArangoDB
    related_courses = []
    student_ids = [s['id'] for s in students]
    
    if student_ids:
        try:
            for student_id in student_ids:
                student_enrollments = db.collection('enrollment').find({'student_id': student_id})
                for enrollment in student_enrollments:
                    rel_course_id = enrollment.get('course_id')
                    if rel_course_id != course_id:
                        # Check if we already have this course in our list
                        existing = next((c for c in related_courses if c['id'] == rel_course_id), None)
                        if existing:
                            existing['shared_students'] += 1
                        else:
                            rel_course_doc = db.collection('courses').find_one({'_id': rel_course_id})
                            if rel_course_doc:
                                related_courses.append({
                                    'id': rel_course_id,
                                    'name': rel_course_doc.get('class_title', 'Unknown Course'),
                                    'shared_students': 1
                                })
            
            # Sort by number of shared students
            related_courses.sort(key=lambda x: x['shared_students'], reverse=True)
        except Exception as e:
            logging.error(f"Error finding related courses from ArangoDB: {str(e)}")
    
    # Calculate grade statistics from ArangoDB data
    grade_stats = {
        'average': 'N/A',
        'median': 'N/A',
        'distribution': {
            'A': 0,
            'B': 0, 
            'C': 0,
            'D': 0,
            'F': 0
        }
    }
    
    grades = [s['grade'] for s in students if s['grade'] not in ('N/A', None)]
    try:
        if grades and all(isinstance(g, (int, float)) for g in grades):
            grade_stats['average'] = round(sum(grades) / len(grades), 1)
            grades.sort()
            mid = len(grades) // 2
            grade_stats['median'] = grades[mid] if len(grades) % 2 else round((grades[mid-1] + grades[mid]) / 2, 1)
            
            # Calculate grade distribution
            for grade in grades:
                if grade >= 90:
                    grade_stats['distribution']['A'] += 1
                elif grade >= 80:
                    grade_stats['distribution']['B'] += 1
                elif grade >= 70:
                    grade_stats['distribution']['C'] += 1
                elif grade >= 60:
                    grade_stats['distribution']['D'] += 1
                else:
                    grade_stats['distribution']['F'] += 1
    except Exception as e:
        logging.error(f"Error calculating grade statistics: {str(e)}")
    
    return render(request, 'network_simulation/course_detail.html', {
        'title': f'Course: {course_data["name"]}',
        'course': course_data,
        'instructors': instructors,
        'students': students,
        'assessments': assessments,
        'related_courses': related_courses,
        'grade_stats': grade_stats
    })