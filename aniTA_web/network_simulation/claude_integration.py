"""
Claude API integration for simulating student assignment feedback.

This module connects to the Claude API to generate realistic feedback on simulated 
student assignments, creating a rich knowledge graph of common mistakes and 
learning recommendations.
"""

import json
import random
import re
from datetime import datetime
from users.arangodb import db
from aniTA_app.claude_service import get_claude_response

# Sample rubric structure for simulated assignments
SAMPLE_RUBRICS = {
    "Quiz": {
        "criteria": [
            {"name": "Understanding of Concepts", "points": 40},
            {"name": "Correct Application", "points": 40},
            {"name": "Clarity of Explanation", "points": 20}
        ],
        "total_points": 100
    },
    "Exam": {
        "criteria": [
            {"name": "Theoretical Understanding", "points": 30},
            {"name": "Problem Solving", "points": 40},
            {"name": "Critical Analysis", "points": 30}
        ],
        "total_points": 100
    },
    "Project": {
        "criteria": [
            {"name": "Research Quality", "points": 25},
            {"name": "Design/Implementation", "points": 35},
            {"name": "Results & Analysis", "points": 25},
            {"name": "Presentation", "points": 15}
        ],
        "total_points": 100
    },
    "Homework": {
        "criteria": [
            {"name": "Completeness", "points": 30},
            {"name": "Correctness", "points": 50},
            {"name": "Presentation", "points": 20}
        ],
        "total_points": 100
    }
}

# Template for source material sections
SOURCE_MATERIAL_TEMPLATE = """
# {title}

## Abstract
{abstract}

## 1. Introduction
{introduction}

## 2. Background
{background}

## 3. Methodology
{methodology}

## 4. Results
{results}

## 5. Discussion
{discussion}

## 6. Conclusion
{conclusion}

## References
{references}
"""

def generate_source_material(course_name, topic):
    """
    Generate source material in research paper format for a given course and topic.
    
    Args:
        course_name: Name of the course
        topic: Topic for the source material
    
    Returns:
        Dictionary containing the source material content and metadata
    """
    prompt = f"""
    Generate a concise research paper on {topic} for a {course_name} course. 
    Structure the paper with these sections:
    1. Abstract (1 paragraph)
    2. Introduction (1-2 paragraphs)
    3. Background (1-2 paragraphs)
    4. Methodology (1-2 paragraphs)
    5. Results (1-2 paragraphs)
    6. Discussion (1-2 paragraphs)
    7. Conclusion (1 paragraph)
    8. References (3-5 references)
    
    Keep each section concise but informative. The entire paper should be suitable for 
    undergraduate students learning this topic for the first time.
    """
    
    try:
        # Call Claude API to generate the content
        response = get_claude_response(prompt)
        
        # Extract sections using regex
        sections = {
            "abstract": extract_section(response, r"Abstract\s*(.*?)(?=\s*\d+\.\s*Introduction|$)", "Abstract not found"),
            "introduction": extract_section(response, r"(?:1\.\s*Introduction|Introduction)\s*(.*?)(?=\s*\d+\.\s*Background|$)", "Introduction not found"),
            "background": extract_section(response, r"(?:2\.\s*Background|Background)\s*(.*?)(?=\s*\d+\.\s*Methodology|$)", "Background not found"),
            "methodology": extract_section(response, r"(?:3\.\s*Methodology|Methodology)\s*(.*?)(?=\s*\d+\.\s*Results|$)", "Methodology not found"),
            "results": extract_section(response, r"(?:4\.\s*Results|Results)\s*(.*?)(?=\s*\d+\.\s*Discussion|$)", "Results not found"),
            "discussion": extract_section(response, r"(?:5\.\s*Discussion|Discussion)\s*(.*?)(?=\s*\d+\.\s*Conclusion|$)", "Discussion not found"),
            "conclusion": extract_section(response, r"(?:6\.\s*Conclusion|Conclusion)\s*(.*?)(?=\s*References|$)", "Conclusion not found"),
            "references": extract_section(response, r"References\s*(.*?)$", "References not found")
        }
        
        # Create the full content
        full_content = SOURCE_MATERIAL_TEMPLATE.format(
            title=f"Understanding {topic} in {course_name}",
            **sections
        )
        
        return {
            "title": f"Understanding {topic} in {course_name}",
            "course": course_name,
            "topic": topic,
            "content": full_content,
            "sections": sections,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating source material: {e}")
        # Fallback to template with placeholder content
        return {
            "title": f"Understanding {topic} in {course_name}",
            "course": course_name,
            "topic": topic,
            "content": SOURCE_MATERIAL_TEMPLATE.format(
                title=f"Understanding {topic} in {course_name}",
                abstract="[Placeholder abstract]",
                introduction="[Placeholder introduction]",
                background="[Placeholder background]",
                methodology="[Placeholder methodology]",
                results="[Placeholder results]",
                discussion="[Placeholder discussion]",
                conclusion="[Placeholder conclusion]",
                references="[Placeholder references]"
            ),
            "sections": {
                "abstract": "[Placeholder abstract]",
                "introduction": "[Placeholder introduction]",
                "background": "[Placeholder background]",
                "methodology": "[Placeholder methodology]",
                "results": "[Placeholder results]",
                "discussion": "[Placeholder discussion]",
                "conclusion": "[Placeholder conclusion]",
                "references": "[Placeholder references]"
            },
            "created_at": datetime.utcnow().isoformat()
        }

def extract_section(text, pattern, default):
    """Extract a section from text using regex pattern."""
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return default

def generate_assignment_instructions(course_name, assignment_type, topic):
    """
    Generate instructions for an assignment using Claude API.
    
    Args:
        course_name: Name of the course
        assignment_type: Type of assignment (Quiz, Exam, Project, Homework)
        topic: Topic for the assignment
    
    Returns:
        Dictionary containing the instructions and metadata
    """
    prompt = f"""
    Generate detailed instructions for a {assignment_type.lower()} assignment on {topic} for a {course_name} course.
    The instructions should include:
    
    1. Assignment overview and objectives
    2. Specific questions or tasks (3-5 items)
    3. Submission requirements
    4. Grading criteria
    
    Make the assignment challenging but appropriate for undergraduate students.
    """
    
    try:
        # Call Claude API to generate the content
        instructions = get_claude_response(prompt)
        
        return {
            "title": f"{topic} {assignment_type}",
            "course": course_name,
            "type": assignment_type,
            "topic": topic,
            "instructions": instructions,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating assignment instructions: {e}")
        # Fallback
        return {
            "title": f"{topic} {assignment_type}",
            "course": course_name,
            "type": assignment_type,
            "topic": topic,
            "instructions": f"This is a {assignment_type.lower()} on {topic} for {course_name}. [Placeholder instructions]",
            "created_at": datetime.utcnow().isoformat()
        }

def generate_sample_answer(assignment_instructions):
    """
    Generate a sample correct answer for an assignment using Claude API.
    
    Args:
        assignment_instructions: The instructions for the assignment
    
    Returns:
        Dictionary containing the sample answer
    """
    prompt = f"""
    For the following assignment, provide a model answer that would receive full credit:
    
    {assignment_instructions}
    
    Your answer should be thorough, accurate, and well-structured.
    """
    
    try:
        # Call Claude API to generate the content
        sample_answer = get_claude_response(prompt)
        
        return {
            "content": sample_answer,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating sample answer: {e}")
        # Fallback
        return {
            "content": "[Placeholder sample answer]",
            "created_at": datetime.utcnow().isoformat()
        }

def generate_student_submission(assignment_instructions, student_level="average"):
    """
    Generate a simulated student submission with deliberate mistakes.
    
    Args:
        assignment_instructions: The instructions for the assignment
        student_level: Quality level of the submission (low, average, high)
    
    Returns:
        Dictionary containing the submission content
    """
    quality_map = {
        "low": "The student has significant gaps in understanding and makes multiple conceptual errors.",
        "average": "The student understands the basics but makes some common mistakes or misconceptions.",
        "high": "The student has a good understanding but makes minor errors or omissions."
    }
    
    quality_description = quality_map.get(student_level, quality_map["average"])
    
    prompt = f"""
    For the following assignment, generate a realistic student submission that demonstrates {student_level} understanding.
    
    Assignment:
    {assignment_instructions}
    
    Guidelines for the submission:
    - {quality_description}
    - Include specific errors or misconceptions that an instructor could provide feedback on
    - Make the submission believable for an undergraduate student
    - The submission should be substantial enough to be graded properly
    """
    
    try:
        # Call Claude API to generate the content
        submission = get_claude_response(prompt)
        
        return {
            "content": submission,
            "quality_level": student_level,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error generating student submission: {e}")
        # Fallback
        return {
            "content": f"[Placeholder {student_level} student submission]",
            "quality_level": student_level,
            "created_at": datetime.utcnow().isoformat()
        }

def generate_feedback_with_rubric(assignment_type, student_submission, sample_answer, source_material):
    """
    Generate instructor feedback for a student submission using Claude API.
    
    Args:
        assignment_type: Type of assignment (Quiz, Exam, Project, Homework)
        student_submission: The student's submission content
        sample_answer: The sample correct answer
        source_material: The source material for the assignment
    
    Returns:
        Dictionary containing the feedback, rubric scores, and identified mistakes
    """
    # Get the rubric for this assignment type
    rubric = SAMPLE_RUBRICS.get(assignment_type, SAMPLE_RUBRICS["Quiz"])
    
    criteria_text = "\n".join([f"- {criterion['name']} ({criterion['points']} points)" for criterion in rubric["criteria"]])
    
    prompt = f"""
    You are grading a student submission for a {assignment_type.lower()}. Please provide detailed feedback and scoring based on the rubric criteria.
    
    RUBRIC CRITERIA:
    {criteria_text}
    Total: {rubric["total_points"]} points
    
    MODEL ANSWER:
    {sample_answer}
    
    SOURCE MATERIAL EXCERPTS:
    Abstract: {source_material["sections"]["abstract"]}
    Key points: 
    - {source_material["sections"]["introduction"][:100]}...
    - {source_material["sections"]["methodology"][:100]}...
    - {source_material["sections"]["conclusion"][:100]}...
    
    STUDENT SUBMISSION:
    {student_submission}
    
    Provide your feedback in the following JSON format:
    ```json
    {{
      "overall_feedback": "Overall assessment of the submission",
      "criteria_scores": [
        {{ 
          "criterion": "Name of criterion 1", 
          "score": 0, 
          "max_points": 0,
          "feedback": "Specific feedback on this criterion"
        }},
        // Additional criteria...
      ],
      "total_score": 0,
      "identified_mistakes": [
        {{
          "mistake": "Description of mistake or misconception 1",
          "correction": "How to correct this mistake",
          "section_reference": "Which section of the source material addresses this (Introduction, Methodology, etc.)"
        }},
        // Additional mistakes...
      ]
    }}
    ```
    
    Ensure your scoring is fair and your feedback is constructive and educational.
    """
    
    try:
        # Call Claude API to generate the feedback
        response = get_claude_response(prompt)
        
        # Extract JSON from the response
        json_str = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_str:
            feedback_data = json.loads(json_str.group(1))
        else:
            # Fallback parsing if the JSON isn't properly formatted
            feedback_data = {
                "overall_feedback": extract_section(response, r"overall_feedback[\"']?\s*:\s*[\"']([^\"']+)[\"']", "Feedback not available"),
                "criteria_scores": [],
                "total_score": extract_section(response, r"total_score[\"']?\s*:\s*(\d+)", "0"),
                "identified_mistakes": []
            }
            
            # Try to extract criteria scores
            criteria_pattern = re.findall(r"criterion[\"']?\s*:\s*[\"']([^\"']+)[\"'].*?score[\"']?\s*:\s*(\d+).*?max_points[\"']?\s*:\s*(\d+).*?feedback[\"']?\s*:\s*[\"']([^\"']+)[\"']", response, re.DOTALL)
            for match in criteria_pattern:
                feedback_data["criteria_scores"].append({
                    "criterion": match[0],
                    "score": int(match[1]),
                    "max_points": int(match[2]),
                    "feedback": match[3]
                })
            
            # Try to extract identified mistakes
            mistakes_pattern = re.findall(r"mistake[\"']?\s*:\s*[\"']([^\"']+)[\"'].*?correction[\"']?\s*:\s*[\"']([^\"']+)[\"'].*?section_reference[\"']?\s*:\s*[\"']([^\"']+)[\"']", response, re.DOTALL)
            for match in mistakes_pattern:
                feedback_data["identified_mistakes"].append({
                    "mistake": match[0],
                    "correction": match[1],
                    "section_reference": match[2]
                })
        
        # Ensure total score is an integer
        if isinstance(feedback_data["total_score"], str):
            feedback_data["total_score"] = int(feedback_data["total_score"])
        
        # Add metadata
        feedback_data["created_at"] = datetime.utcnow().isoformat()
        
        return feedback_data
        
    except Exception as e:
        print(f"Error generating feedback: {e}")
        # Fallback
        return {
            "overall_feedback": "This submission shows some understanding but has several areas for improvement.",
            "criteria_scores": [
                {
                    "criterion": criterion["name"],
                    "score": int(criterion["points"] * 0.7),  # 70% score as fallback
                    "max_points": criterion["points"],
                    "feedback": f"The {criterion['name'].lower()} needs improvement."
                }
                for criterion in rubric["criteria"]
            ],
            "total_score": int(rubric["total_points"] * 0.7),  # 70% total score
            "identified_mistakes": [
                {
                    "mistake": "Conceptual misunderstanding",
                    "correction": "Review the core concepts in the material",
                    "section_reference": "Introduction"
                },
                {
                    "mistake": "Incomplete analysis",
                    "correction": "Consider all aspects discussed in the methodology",
                    "section_reference": "Methodology"
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }

def store_source_material(source_material):
    """
    Store source material in ArangoDB and create section documents.
    
    Args:
        source_material: Source material document
    
    Returns:
        Dictionary with material_id and section_ids
    """
    # Store the full source material
    course_materials = db.collection('course_materials')
    
    # Create the course material document
    material_data = {
        "title": source_material["title"],
        "course": source_material["course"],
        "topic": source_material["topic"],
        "content": source_material["content"],
        "created_at": source_material["created_at"],
        "is_simulated": True
    }
    
    material_id = course_materials.insert(material_data)["_id"]
    
    # Create section documents
    sections_collection = db.collection('sections')
    section_ids = {}
    
    for section_name, content in source_material["sections"].items():
        section_data = {
            "title": section_name.capitalize(),
            "content": content,
            "material_id": material_id,
            "class_code": source_material["course"].replace(" ", ""),
            "created_at": datetime.utcnow().isoformat(),
            "is_simulated": True
        }
        
        section_id = sections_collection.insert(section_data)["_id"]
        section_ids[section_name] = section_id
    
    return {
        "material_id": material_id,
        "section_ids": section_ids
    }

def store_assignment_with_rubric(course_id, assignment_data, source_material_ids):
    """
    Store assignment, sample answer, and rubric in ArangoDB.
    
    Args:
        course_id: ArangoDB ID of the course
        assignment_data: Assignment instructions and metadata
        source_material_ids: IDs of the source material documents
    
    Returns:
        Assignment ID
    """
    # Get course
    courses = db.collection('courses')
    course = courses.get(course_id)
    
    if not course:
        print(f"Course not found: {course_id}")
        return None
    
    # Get appropriate rubric
    rubric_data = SAMPLE_RUBRICS.get(assignment_data["type"], SAMPLE_RUBRICS["Quiz"])
    
    # Create rubric
    rubrics = db.collection('rubrics')
    rubric_doc = {
        "title": f"Rubric for {assignment_data['title']}",
        "criteria": rubric_data["criteria"],
        "total_points": rubric_data["total_points"],
        "course_id": course_id,
        "created_at": datetime.utcnow().isoformat(),
        "is_simulated": True
    }
    
    rubric_id = rubrics.insert(rubric_doc)["_id"]
    
    # Create relationship between rubric and course
    has_rubric = db.collection('has_rubric')
    has_rubric.insert({
        "_from": course_id,
        "_to": rubric_id,
        "created_at": datetime.utcnow().isoformat(),
        "is_simulated": True
    })
    
    # Add to course assignments
    assignment_id = f"{course['class_code']}_{assignment_data['type']}_{random.randint(1000, 9999)}"
    
    new_assignment = {
        "id": assignment_id,
        "name": assignment_data["title"],
        "description": assignment_data["instructions"][:200] + "...",
        "due_date": (datetime.utcnow().isoformat().split("T")[0]),
        "total_points": rubric_data["total_points"],
        "created_at": datetime.utcnow().isoformat(),
        "rubric_id": rubric_id,
        "source_material_id": source_material_ids["material_id"],
        "is_simulated": True
    }
    
    if "assignments" not in course:
        course["assignments"] = []
    
    course["assignments"].append(new_assignment)
    courses.update(course)
    
    # Create relationships between rubric and source material sections
    for section_name, section_id in source_material_ids["section_ids"].items():
        related_to = db.collection('related_to')
        related_to.insert({
            "_from": rubric_id,
            "_to": section_id,
            "relationship_type": "references",
            "strength": random.uniform(0.5, 1.0),
            "created_at": datetime.utcnow().isoformat(),
            "is_simulated": True
        })
    
    return assignment_id

def process_student_submission(student_id, course_id, assignment_id, submission_data, source_material_ids, feedback_data):
    """
    Process a student submission with feedback and create the knowledge graph connections.
    
    Args:
        student_id: ArangoDB ID of the student
        course_id: ArangoDB ID of the course
        assignment_id: ID of the assignment
        submission_data: Student submission content
        source_material_ids: IDs of the source material documents
        feedback_data: Feedback from Claude API
    
    Returns:
        Submission ID
    """
    # Create submission record
    submissions = db.collection('submission')
    
    submission_doc = {
        "user_id": student_id,
        "class_code": db.collection('courses').get(course_id)["class_code"],
        "assignment_id": assignment_id,
        "file_name": f"simulated_submission_{random.randint(1000, 9999)}.pdf",
        "file_content": submission_data["content"],
        "submission_date": datetime.utcnow().isoformat(),
        "grade": feedback_data["total_score"],
        "feedback": feedback_data["overall_feedback"],
        "graded": True,
        "ai_score": feedback_data["total_score"],
        "ai_feedback": json.dumps(feedback_data),
        "is_simulated": True
    }
    
    submission_id = submissions.insert(submission_doc)["_id"]
    
    # Process identified mistakes
    mistakes = db.collection('mistakes')
    made_mistake = db.collection('made_mistake')
    related_to = db.collection('related_to')
    
    for mistake_data in feedback_data["identified_mistakes"]:
        # Create mistake document
        mistake_doc = {
            "question": mistake_data["mistake"],
            "justification": mistake_data["correction"],
            "score_awarded": 0,  # Represents points lost due to mistake
            "rubric_criteria_names": [criterion["criterion"] for criterion in feedback_data["criteria_scores"]],
            "created_at": datetime.utcnow().isoformat(),
            "is_simulated": True
        }
        
        mistake_id = mistakes.insert(mistake_doc)["_id"]
        
        # Connect student to mistake
        made_mistake.insert({
            "_from": student_id,
            "_to": mistake_id,
            "created_at": datetime.utcnow().isoformat(),
            "is_simulated": True
        })
        
        # Connect mistake to submission
        has_feedback_on = db.collection('has_feedback_on')
        has_feedback_on.insert({
            "_from": submission_id,
            "_to": mistake_id,
            "created_at": datetime.utcnow().isoformat(),
            "is_simulated": True
        })
        
        # Connect mistake to relevant section of source material
        section_reference = mistake_data["section_reference"].lower()
        # Find closest matching section
        matching_section = None
        for section_name, section_id in source_material_ids["section_ids"].items():
            if section_reference in section_name.lower() or section_name.lower() in section_reference:
                matching_section = section_id
                break
        
        # If no exact match, use introduction as fallback
        if not matching_section and "introduction" in source_material_ids["section_ids"]:
            matching_section = source_material_ids["section_ids"]["introduction"]
        
        if matching_section:
            related_to.insert({
                "_from": mistake_id,
                "_to": matching_section,
                "relationship_type": "explained_in",
                "strength": random.uniform(0.7, 1.0),
                "created_at": datetime.utcnow().isoformat(),
                "is_simulated": True
            })
    
    return submission_id

def create_simulated_assignment_workflow(course_name, topic, num_students=5):
    """
    Create a complete simulated assignment workflow with source material,
    assignment, submissions, and feedback.
    
    Args:
        course_name: Name of the course
        topic: Topic for the assignment
        num_students: Number of student submissions to simulate
    
    Returns:
        Dictionary with IDs of created documents
    """
    try:
        # 1. Find the course in ArangoDB
        courses = db.collection('courses')
        course_query = f"""
        FOR c IN courses
            FILTER LOWER(c.class_title) LIKE LOWER("%{course_name}%")
            LIMIT 1
            RETURN c
        """
        course_list = list(db.aql.execute(course_query))
        
        if not course_list:
            print(f"Course not found: {course_name}")
            return None
        
        course = course_list[0]
        course_id = course["_id"]
        
        # 2. Generate and store source material
        assignment_type = random.choice(["Quiz", "Exam", "Project", "Homework"])
        source_material = generate_source_material(course_name, topic)
        source_material_ids = store_source_material(source_material)
        
        # 3. Generate and store assignment
        assignment_instructions = generate_assignment_instructions(course_name, assignment_type, topic)
        assignment_id = store_assignment_with_rubric(course_id, assignment_instructions, source_material_ids)
        
        # 4. Generate sample answer
        sample_answer = generate_sample_answer(assignment_instructions["instructions"])
        
        # 5. Find students for this course
        users = db.collection('users')
        student_query = f"""
        FOR u IN users
            FILTER u.role == "student" AND u.is_simulated == true
            FILTER HAS(u, "courses") AND "{course['class_code']}" IN u.courses
            LIMIT {num_students}
            RETURN u
        """
        students = list(db.aql.execute(student_query))
        
        # If not enough students found, find any simulated students
        if len(students) < num_students:
            additional_query = f"""
            FOR u IN users
                FILTER u.role == "student" AND u.is_simulated == true
                LIMIT {num_students - len(students)}
                RETURN u
            """
            students.extend(list(db.aql.execute(additional_query)))
        
        # 6. Process student submissions
        submission_ids = []
        for i, student in enumerate(students):
            # Select quality level based on student's position in sequence
            if i < num_students * 0.2:  # Top 20%
                quality = "high"
            elif i < num_students * 0.7:  # Next 50%
                quality = "average"
            else:  # Bottom 30%
                quality = "low"
            
            # Generate submission
            submission = generate_student_submission(assignment_instructions["instructions"], quality)
            
            # Generate feedback
            feedback = generate_feedback_with_rubric(
                assignment_type,
                submission["content"],
                sample_answer["content"],
                source_material
            )
            
            # Process submission
            submission_id = process_student_submission(
                student["_id"],
                course_id,
                assignment_id,
                submission,
                source_material_ids,
                feedback
            )
            
            submission_ids.append(submission_id)
            
            # Add course to student if not already enrolled
            if "courses" not in student or course["class_code"] not in student["courses"]:
                if "courses" not in student:
                    student["courses"] = []
                student["courses"].append(course["class_code"])
                users.update(student)
        
        return {
            "course_id": course_id,
            "source_material_id": source_material_ids["material_id"],
            "assignment_id": assignment_id,
            "submission_ids": submission_ids
        }
        
    except Exception as e:
        print(f"Error in assignment workflow: {e}")
        return None

def rank_sections_by_pagerank():
    """
    Apply PageRank algorithm to rank sections based on their connections to mistakes.
    
    Returns:
        Dictionary mapping section IDs to their PageRank scores
    """
    # Query to build a directed graph connecting sections through mistakes
    query = """
    LET sections = (
        FOR s IN sections
        FILTER s.is_simulated == true
        RETURN s
    )
    
    LET edges = (
        FOR m IN mistakes
        FILTER m.is_simulated == true
        FOR e1 IN related_to
            FILTER e1._from == m._id
            FOR s IN sections
                FILTER s._id == e1._to
                RETURN {
                    source: m._id,
                    target: s._id,
                    weight: e1.strength ? e1.strength : 1.0
                }
    )
    
    RETURN { sections: sections, edges: edges }
    """
    
    graph_data = list(db.aql.execute(query))[0]
    
    # Build NetworkX graph
    import networkx as nx
    G = nx.DiGraph()
    
    # Add all section nodes
    for section in graph_data["sections"]:
        G.add_node(section["_id"], title=section["title"], content=section.get("content", ""))
    
    # Add edges
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
    
    # Apply PageRank
    pagerank = nx.pagerank(G, weight='weight')
    
    # Update sections with PageRank scores
    sections_collection = db.collection('sections')
    for section_id, score in pagerank.items():
        # Only update sections, not mistakes
        if section_id.startswith("sections/"):
            section = sections_collection.get(section_id)
            if section:
                section["pagerank_score"] = score
                sections_collection.update(section)
    
    return pagerank

def get_top_sections_for_student(student_id, limit=5):
    """
    Get the top recommended sections for a student based on their mistakes.
    
    Args:
        student_id: ArangoDB ID of the student
        limit: Maximum number of sections to return
    
    Returns:
        List of section documents with scores
    """
    query = """
    FOR edge IN made_mistake
        FILTER edge._from == @student_id AND edge.is_simulated == true
        FOR mistake IN mistakes
            FILTER mistake._id == edge._to
            FOR rel IN related_to
                FILTER rel._from == mistake._id
                FOR section IN sections
                    FILTER section._id == rel._to
                    
                    COLLECT 
                        section_id = section._id,
                        title = section.title,
                        content = section.content,
                        material_id = section.material_id,
                        pagerank = section.pagerank_score ? section.pagerank_score : 0
                    AGGREGATE
                        relevance = COUNT(),
                        avg_strength = AVERAGE(rel.strength ? rel.strength : 0.5)
                    
                    // Final score combines relevance, relationship strength, and PageRank
                    LET score = (relevance * 0.4) + (avg_strength * 0.3) + (pagerank * 10 * 0.3)
                    
                    SORT score DESC
                    LIMIT @limit
                    
                    FOR material IN course_materials
                        FILTER material._id == material_id
                        
                        RETURN {
                            "id": section_id,
                            "title": title,
                            "content_preview": LEFT(content, 200) + "...",
                            "material_title": material.title,
                            "score": score,
                            "relevance_count": relevance,
                            "pagerank": pagerank
                        }
    """
    
    try:
        sections = list(db.aql.execute(
            query, 
            bind_vars={"student_id": student_id, "limit": limit}
        ))
        
        return sections
    except Exception as e:
        print(f"Error getting top sections: {e}")
        return []

def get_problematic_sections_for_instructor(instructor_id, limit=5):
    """
    Get the sections where students are making the most mistakes for an instructor.
    
    Args:
        instructor_id: ArangoDB ID of the instructor
        limit: Maximum number of sections to return
    
    Returns:
        List of section documents with mistake counts
    """
    query = """
    FOR course IN courses
        FILTER course.instructor_id == @instructor_id AND course.is_simulated == true
        
        FOR submission IN submission
            FILTER submission.class_code == course.class_code AND submission.is_simulated == true
            
            FOR feedback IN has_feedback_on
                FILTER feedback._from == submission._id
                FOR mistake IN mistakes
                    FILTER mistake._id == feedback._to
                    FOR relation IN related_to
                        FILTER relation._from == mistake._id
                        FOR section IN sections
                            FILTER section._id == relation._to
                            
                            COLLECT 
                                section_id = section._id,
                                title = section.title,
                                content = section.content,
                                material_id = section.material_id,
                                course_code = course.class_code,
                                course_title = course.class_title
                            AGGREGATE
                                mistake_count = COUNT(),
                                students = COUNT(DISTINCT submission.user_id)
                            
                            SORT mistake_count DESC
                            LIMIT @limit
                            
                            FOR material IN course_materials
                                FILTER material._id == material_id
                                
                                RETURN {
                                    "id": section_id,
                                    "title": title,
                                    "content_preview": LEFT(content, 200) + "...",
                                    "material_title": material.title,
                                    "course": course_title,
                                    "course_code": course_code,
                                    "mistake_count": mistake_count,
                                    "student_count": students,
                                    "percentage": (students / (
                                        FOR s IN submission
                                            FILTER s.class_code == course_code
                                            COLLECT AGGREGATE count = COUNT(DISTINCT s.user_id)
                                            RETURN count
                                    )[0]) * 100
                                }
    """
    
    try:
        sections = list(db.aql.execute(
            query, 
            bind_vars={"instructor_id": instructor_id, "limit": limit}
        ))
        
        return sections
    except Exception as e:
        print(f"Error getting problematic sections: {e}")
        return []