"""
ArangoDB-based network analysis functions.

This module provides network analysis functions that use ArangoDB's graph capabilities
for educational analytics, including:
- Consistency in grading
- Student weaknesses detection
- Instructor feedback patterns
- Course relationship analysis
"""

from users.arangodb import db
import json

def get_student_instructor_network():
    """
    Query ArangoDB to get student-instructor network data.
    Returns data formatted for visualization.
    """
    # Query to find connections between students and instructors through submissions
    query = """
    FOR student IN users
        FILTER student.role == "student" AND student.is_simulated == true
        FOR submission IN submission
            FILTER submission.user_id == student._id
            FOR course IN courses
                FILTER course.class_code == submission.class_code
                FOR instructor IN users
                    FILTER instructor._id == course.instructor_id AND instructor.role == "instructor"
                    
                    COLLECT 
                        student_id = student._id, 
                        student_name = student.username, 
                        instructor_id = instructor._id,
                        instructor_name = instructor.username
                    
                    AGGREGATE 
                        submission_count = COUNT(),
                        avg_grade = AVERAGE(submission.grade)
                    
                    RETURN {
                        "from": { 
                            "id": student_id, 
                            "name": student_name, 
                            "type": "student" 
                        },
                        "to": { 
                            "id": instructor_id, 
                            "name": instructor_name, 
                            "type": "instructor" 
                        },
                        "weight": submission_count,
                        "avg_grade": avg_grade
                    }
    """
    results = list(db.aql.execute(query))
    
    # Format for visualization
    nodes = []
    edges = []
    node_map = {}  # To avoid duplicates
    
    for connection in results:
        # Add student node if not already added
        if connection['from']['id'] not in node_map:
            node_map[connection['from']['id']] = len(nodes)
            nodes.append({
                'id': connection['from']['id'],
                'name': connection['from']['name'],
                'type': 'student'
            })
        
        # Add instructor node if not already added
        if connection['to']['id'] not in node_map:
            node_map[connection['to']['id']] = len(nodes)
            nodes.append({
                'id': connection['to']['id'],
                'name': connection['to']['name'],
                'type': 'instructor'
            })
        
        # Add the edge
        edges.append({
            'source': node_map[connection['from']['id']],
            'target': node_map[connection['to']['id']],
            'weight': connection['weight'],
            'grade': connection['avg_grade']
        })
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def get_course_network():
    """
    Query ArangoDB to get course network data based on shared students.
    Returns data formatted for visualization.
    """
    # Query to find courses that share students
    query = """
    FOR student IN users
        FILTER student.role == "student" AND student.is_simulated == true
        FILTER HAS(student, "courses") AND LENGTH(student.courses) >= 2
        
        LET courses = student.courses
        FOR i IN 0..LENGTH(courses)-2
            FOR j IN i+1..LENGTH(courses)-1
                COLLECT 
                    course1 = courses[i], 
                    course2 = courses[j]
                AGGREGATE 
                    shared_count = COUNT()
                    
                FOR c1 IN courses
                    FILTER c1 == course1
                    FOR c2 IN courses
                        FILTER c2 == course2
                        FOR courseDoc1 IN courses
                            FILTER courseDoc1.class_code == c1
                            FOR courseDoc2 IN courses
                                FILTER courseDoc2.class_code == c2
                                
                                RETURN {
                                    "from": { 
                                        "id": c1, 
                                        "name": courseDoc1.class_title, 
                                        "type": "course" 
                                    },
                                    "to": { 
                                        "id": c2, 
                                        "name": courseDoc2.class_title, 
                                        "type": "course" 
                                    },
                                    "shared_students": shared_count
                                }
    """
    
    # Alternative query if the above complex query doesn't work
    simple_query = """
    FOR student IN users
        FILTER student.role == "student" AND student.is_simulated == true
        FILTER HAS(student, "courses") AND LENGTH(student.courses) >= 2
        
        FOR c1 IN student.courses
            FOR c2 IN student.courses
                FILTER c1 < c2
                
                COLLECT course1 = c1, course2 = c2
                AGGREGATE count = COUNT()
                
                LET course1Doc = FIRST(FOR c IN courses FILTER c.class_code == course1 RETURN c)
                LET course2Doc = FIRST(FOR c IN courses FILTER c.class_code == course2 RETURN c)
                
                FILTER course1Doc != null AND course2Doc != null
                
                RETURN {
                    "from": {
                        "id": course1,
                        "name": course1Doc.class_title,
                        "type": "course"
                    },
                    "to": {
                        "id": course2,
                        "name": course2Doc.class_title,
                        "type": "course"
                    },
                    "shared_students": count
                }
    """
    
    try:
        results = list(db.aql.execute(simple_query))
    except Exception as e:
        print(f"Error in course network query: {e}")
        results = []
    
    # Format for visualization
    nodes = []
    edges = []
    node_map = {}  # To avoid duplicates
    
    for connection in results:
        # Add course1 node if not already added
        if connection['from']['id'] not in node_map:
            node_map[connection['from']['id']] = len(nodes)
            nodes.append({
                'id': connection['from']['id'],
                'name': connection['from']['name'],
                'type': 'course'
            })
        
        # Add course2 node if not already added
        if connection['to']['id'] not in node_map:
            node_map[connection['to']['id']] = len(nodes)
            nodes.append({
                'id': connection['to']['id'],
                'name': connection['to']['name'],
                'type': 'course'
            })
        
        # Add the edge
        edges.append({
            'source': node_map[connection['from']['id']],
            'target': node_map[connection['to']['id']],
            'weight': connection['shared_students']
        })
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def detect_grading_inconsistencies(instructor_id=None):
    """
    Detect potential grading inconsistencies across instructors.
    
    Args:
        instructor_id: Optional instructor ID to filter results
    
    Returns:
        List of potential inconsistencies
    """
    # Query to find similar submissions with significantly different grades
    query = """
    FOR sub1 IN submission
        FILTER sub1.is_simulated == true
        
        FOR sub2 IN submission
            FILTER sub2.is_simulated == true
            FILTER sub1._id != sub2._id
            FILTER sub1.assignment_id == sub2.assignment_id
            FILTER ABS(sub1.grade - sub2.grade) > 15
            
            LET student1 = DOCUMENT(sub1.user_id)
            LET student2 = DOCUMENT(sub2.user_id)
            LET course = FIRST(FOR c IN courses FILTER c.class_code == sub1.class_code RETURN c)
            LET instructor = DOCUMENT(course.instructor_id)
            
            FILTER instructor != null
    """
    
    # Add instructor filter if provided
    if instructor_id:
        query += f"""
            FILTER instructor._id == "{instructor_id}"
        """
    
    query += """
            RETURN {
                "course": course.class_title,
                "assignment_id": sub1.assignment_id,
                "inconsistency": {
                    "student1": {
                        "name": student1.username,
                        "grade": sub1.grade
                    },
                    "student2": {
                        "name": student2.username,
                        "grade": sub2.grade
                    },
                    "difference": ABS(sub1.grade - sub2.grade)
                },
                "instructor": instructor.username
            }
    """
    
    try:
        results = list(db.aql.execute(query))
        
        # Group by course and assignment to avoid duplicates
        grouped = {}
        for item in results:
            key = f"{item['course']}_{item['assignment_id']}"
            if key not in grouped or item['inconsistency']['difference'] > grouped[key]['inconsistency']['difference']:
                grouped[key] = item
        
        return list(grouped.values())
    except Exception as e:
        print(f"Error detecting grading inconsistencies: {e}")
        return []

def get_student_weaknesses(student_id):
    """
    Identify a student's weak areas based on grades and mistake patterns.
    
    Args:
        student_id: Student's ArangoDB ID
    
    Returns:
        Dictionary of weakness areas with recommendations
    """
    # Query to find areas where the student has lower grades
    grade_query = """
    FOR submission IN submission
        FILTER submission.user_id == @student_id AND submission.is_simulated == true
        
        LET course = FIRST(FOR c IN courses FILTER c.class_code == submission.class_code RETURN c)
        
        COLLECT 
            assignment_type = REGEX_EXTRACT(submission.assignment_id, ".*_([^_]+)_.*", 1)[0]
        AGGREGATE
            avg_grade = AVERAGE(submission.grade),
            count = COUNT()
        
        SORT avg_grade ASC
        LIMIT 3
        
        RETURN {
            "type": assignment_type,
            "avg_grade": avg_grade,
            "count": count
        }
    """
    
    # Query to find mistakes the student has made
    mistake_query = """
    FOR edge IN made_mistake
        FILTER edge._from == @student_id AND edge.is_simulated == true
        
        FOR mistake IN mistakes
            FILTER mistake._id == edge._to
            
            COLLECT 
                topic = mistake.question,
                justification = mistake.justification
            AGGREGATE
                count = COUNT()
            
            SORT count DESC
            LIMIT 5
            
            RETURN {
                "topic": topic,
                "justification": justification,
                "count": count
            }
    """
    
    try:
        grade_results = list(db.aql.execute(
            grade_query, 
            bind_vars={"student_id": student_id}
        ))
        
        mistake_results = list(db.aql.execute(
            mistake_query, 
            bind_vars={"student_id": student_id}
        ))
        
        # Generate personalized recommendations
        recommendations = []
        for weakness in grade_results:
            focus_area = {
                "type": weakness["type"],
                "avg_grade": weakness["avg_grade"],
                "recommendation": f"Focus on improving your performance in {weakness['type']} assignments"
            }
            
            # Add specific recommendations based on mistake patterns
            related_mistakes = [m for m in mistake_results 
                               if m["topic"].lower() in weakness["type"].lower() 
                               or weakness["type"].lower() in m["topic"].lower()]
            
            if related_mistakes:
                focus_area["related_issues"] = related_mistakes
                focus_area["detailed_recommendation"] = f"Pay special attention to {related_mistakes[0]['topic']} concepts"
            
            recommendations.append(focus_area)
        
        return {
            "weak_areas": grade_results,
            "common_mistakes": mistake_results,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error identifying student weaknesses: {e}")
        return {"error": str(e)}

def get_instructor_teaching_insights(instructor_id):
    """
    Generate teaching insights for an instructor based on student performance.
    
    Args:
        instructor_id: Instructor's ArangoDB ID
    
    Returns:
        Dictionary of insights and recommendations
    """
    # Query to get courses taught by this instructor
    courses_query = """
    FOR course IN courses
        FILTER course.instructor_id == @instructor_id AND course.is_simulated == true
        RETURN {
            "code": course.class_code,
            "title": course.class_title
        }
    """
    
    # Query to get grade distribution by course
    grade_query = """
    FOR course IN courses
        FILTER course.instructor_id == @instructor_id AND course.is_simulated == true
        
        LET submissions = (
            FOR sub IN submission
                FILTER sub.class_code == course.class_code AND sub.is_simulated == true
                RETURN sub
        )
        
        LET avg_grade = AVERAGE(submissions[*].grade)
        LET assignments = (
            FOR sub IN submissions
                COLLECT assignment = sub.assignment_id
                AGGREGATE avg = AVERAGE(sub.grade)
                RETURN {
                    "id": assignment,
                    "avg": avg
                }
        )
        
        RETURN {
            "course": course.class_title,
            "code": course.class_code,
            "avg_grade": avg_grade,
            "submission_count": LENGTH(submissions),
            "assignments": assignments
        }
    """
    
    # Query to find common mistakes across this instructor's courses
    mistake_query = """
    FOR course IN courses
        FILTER course.instructor_id == @instructor_id AND course.is_simulated == true
        
        FOR sub IN submission
            FILTER sub.class_code == course.class_code AND sub.is_simulated == true
            
            FOR student IN users
                FILTER student._id == sub.user_id
                
                FOR edge IN made_mistake
                    FILTER edge._from == student._id AND edge.is_simulated == true
                    
                    FOR mistake IN mistakes
                        FILTER mistake._id == edge._to
                        
                        COLLECT 
                            topic = mistake.question,
                            justification = mistake.justification
                        AGGREGATE
                            count = COUNT()
                        
                        SORT count DESC
                        LIMIT 8
                        
                        RETURN {
                            "topic": topic,
                            "justification": justification,
                            "count": count
                        }
    """
    
    try:
        courses = list(db.aql.execute(
            courses_query, 
            bind_vars={"instructor_id": instructor_id}
        ))
        
        grade_stats = list(db.aql.execute(
            grade_query, 
            bind_vars={"instructor_id": instructor_id}
        ))
        
        common_mistakes = list(db.aql.execute(
            mistake_query, 
            bind_vars={"instructor_id": instructor_id}
        ))
        
        # Generate course-specific insights
        course_insights = []
        for course_stat in grade_stats:
            # Find assignments with notably lower average grades
            avg_course_grade = course_stat["avg_grade"]
            problematic_assignments = []
            
            for assignment in course_stat.get("assignments", []):
                if assignment["avg"] < avg_course_grade - 10:
                    problematic_assignments.append(assignment)
            
            insight = {
                "course": course_stat["course"],
                "code": course_stat["code"],
                "avg_grade": course_stat["avg_grade"],
                "submission_count": course_stat["submission_count"]
            }
            
            if problematic_assignments:
                insight["problematic_assignments"] = problematic_assignments
                insight["recommendation"] = "Consider reviewing the content or assessment criteria for these assignments"
            
            course_insights.append(insight)
        
        # Generate general teaching recommendations based on common mistakes
        teaching_recommendations = []
        
        if common_mistakes:
            for mistake in common_mistakes[:3]:  # Top 3 most common mistakes
                recommendation = {
                    "issue": mistake["topic"],
                    "description": mistake["justification"],
                    "frequency": mistake["count"],
                    "suggestion": f"Consider focusing more classroom time on {mistake['topic']}"
                }
                teaching_recommendations.append(recommendation)
        
        return {
            "courses": courses,
            "course_insights": course_insights,
            "common_mistakes": common_mistakes,
            "teaching_recommendations": teaching_recommendations,
            "grading_inconsistencies": detect_grading_inconsistencies(instructor_id)
        }
    except Exception as e:
        print(f"Error generating instructor insights: {e}")
        return {"error": str(e)}

def get_course_material_recommendations(student_id):
    """
    Generate personalized course material recommendations for a student.
    
    Args:
        student_id: Student's ArangoDB ID
    
    Returns:
        List of recommended materials
    """
    # Query to find appropriate course materials based on student's mistakes
    query = """
    FOR edge IN made_mistake
        FILTER edge._from == @student_id AND edge.is_simulated == true
        
        FOR mistake IN mistakes
            FILTER mistake._id == edge._to
            
            // Find course materials that relate to these mistake areas
            FOR material IN course_materials
                // Simple relevance matching based on title/description and mistake topics
                LET relevance = (
                    LIKE(LOWER(material.title), CONCAT("%", LOWER(mistake.question), "%")) ? 2 : 0
                ) + (
                    LIKE(LOWER(material.description), CONCAT("%", LOWER(mistake.question), "%")) ? 1 : 0
                )
                
                FILTER relevance > 0
                
                COLLECT 
                    id = material._id,
                    title = material.title,
                    description = material.description
                AGGREGATE
                    score = SUM(relevance)
                
                SORT score DESC
                LIMIT 5
                
                RETURN {
                    "id": id,
                    "title": title,
                    "description": description,
                    "relevance_score": score
                }
    """
    
    # Alternative approach if no materials available - create simulated recommendations
    fallback_query = """
    FOR edge IN made_mistake
        FILTER edge._from == @student_id AND edge.is_simulated == true
        
        FOR mistake IN mistakes
            FILTER mistake._id == edge._to
            
            COLLECT 
                topic = mistake.question
            AGGREGATE
                count = COUNT()
            
            SORT count DESC
            LIMIT 5
            
            RETURN {
                "topic": topic,
                "count": count
            }
    """
    
    try:
        recommendations = list(db.aql.execute(
            query, 
            bind_vars={"student_id": student_id}
        ))
        
        # If no real materials found, generate simulated recommendations
        if not recommendations:
            topics = list(db.aql.execute(
                fallback_query, 
                bind_vars={"student_id": student_id}
            ))
            
            for i, topic in enumerate(topics):
                recommendations.append({
                    "id": f"sim_{i}",
                    "title": f"{topic['topic']} Fundamentals",
                    "description": f"Key concepts and practical applications of {topic['topic']}",
                    "relevance_score": topic['count'],
                    "simulated": True
                })
        
        return recommendations
    except Exception as e:
        print(f"Error generating course material recommendations: {e}")
        return []