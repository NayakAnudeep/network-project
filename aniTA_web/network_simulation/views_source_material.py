"""
Views for source materials and section recommendations.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from users.arangodb import db
from .claude_integration import (
    get_top_sections_for_student,
    get_problematic_sections_for_instructor
)
from .markdown_wrapper import convert_markdown_to_html
import re

@login_required
def source_materials_list(request):
    """View for listing all source materials."""
    try:
        # Query to get all source materials
        query = """
        FOR material IN course_materials
            FILTER material.is_simulated == true
            SORT material.created_at DESC
            LET course = FIRST(
                FOR c IN courses
                    FILTER c.class_code == material.course
                    RETURN c
            )
            RETURN {
                "id": material._id,
                "title": material.title,
                "course": material.course,
                "course_title": course ? course.class_title : material.course,
                "topic": material.topic,
                "created_at": material.created_at
            }
        """
        materials = list(db.aql.execute(query))
        
        context = {
            'materials': materials,
            'title': 'Source Materials'
        }
        
        return render(request, 'network_simulation/source_materials_list.html', context)
    
    except Exception as e:
        context = {
            'error': str(e),
            'title': 'Source Materials - Error'
        }
        return render(request, 'network_simulation/error.html', context)

@login_required
def source_material_detail(request, material_id):
    """View for displaying a single source material with all its sections."""
    try:
        # Get the source material
        material_query = """
        FOR material IN course_materials
            FILTER material._id == @material_id
            RETURN material
        """
        
        materials = list(db.aql.execute(
            material_query,
            bind_vars={"material_id": material_id}
        ))
        
        if not materials:
            raise Http404("Source material not found")
        
        material = materials[0]
        
        # Get the sections
        sections_query = """
        FOR section IN sections
            FILTER section.material_id == @material_id
            SORT section.title ASC
            RETURN {
                "id": section._id,
                "title": section.title,
                "content": section.content,
                "pagerank_score": section.pagerank_score
            }
        """
        
        sections = list(db.aql.execute(
            sections_query,
            bind_vars={"material_id": material_id}
        ))
        
        # Convert markdown content to HTML
        material_content_html = convert_markdown_to_html(material.get('content', ''))
        
        for section in sections:
            section['html_content'] = convert_markdown_to_html(section.get('content', ''))
        
        context = {
            'material': material,
            'html_content': material_content_html,
            'sections': sections,
            'title': material.get('title', 'Source Material')
        }
        
        return render(request, 'network_simulation/source_material_detail.html', context)
    
    except Http404:
        raise
    except Exception as e:
        context = {
            'error': str(e),
            'title': 'Source Material - Error'
        }
        return render(request, 'network_simulation/error.html', context)

@login_required
def section_detail(request, section_id):
    """View for displaying a single section with related information."""
    try:
        # Get the section
        section_query = """
        FOR section IN sections
            FILTER section._id == @section_id
            LET material = FIRST(
                FOR m IN course_materials
                    FILTER m._id == section.material_id
                    RETURN m
            )
            LET related_mistakes = (
                FOR rel IN related_to
                    FILTER rel._to == section._id
                    FOR mistake IN mistakes
                        FILTER mistake._id == rel._from
                        RETURN {
                            "id": mistake._id,
                            "question": mistake.question,
                            "justification": mistake.justification,
                            "strength": rel.strength
                        }
            )
            RETURN {
                "id": section._id,
                "title": section.title,
                "content": section.content,
                "material_id": section.material_id,
                "material_title": material.title,
                "pagerank_score": section.pagerank_score,
                "related_mistakes": related_mistakes
            }
        """
        
        sections = list(db.aql.execute(
            section_query,
            bind_vars={"section_id": section_id}
        ))
        
        if not sections:
            raise Http404("Section not found")
        
        section = sections[0]
        
        # Convert markdown content to HTML
        section_content_html = convert_markdown_to_html(section.get('content', ''))
        
        # Get students who should focus on this section (made related mistakes)
        students_query = """
        FOR rel IN related_to
            FILTER rel._to == @section_id
            FOR mistake IN mistakes
                FILTER mistake._id == rel._from
                FOR edge IN made_mistake
                    FILTER edge._to == mistake._id
                    FOR student IN users
                        FILTER student._id == edge._from AND student.role == "student"
                        COLLECT 
                            id = student._id,
                            name = student.username
                        AGGREGATE 
                            mistake_count = COUNT()
                        SORT mistake_count DESC
                        LIMIT 10
                        RETURN {
                            "id": id,
                            "name": name,
                            "mistake_count": mistake_count
                        }
        """
        
        students = list(db.aql.execute(
            students_query,
            bind_vars={"section_id": section_id}
        ))
        
        context = {
            'section': section,
            'html_content': section_content_html,
            'students': students,
            'title': section.get('title', 'Section Detail')
        }
        
        return render(request, 'network_simulation/section_detail.html', context)
    
    except Http404:
        raise
    except Exception as e:
        context = {
            'error': str(e),
            'title': 'Section Detail - Error'
        }
        return render(request, 'network_simulation/error.html', context)

@login_required
def student_section_recommendations(request, student_id):
    """View for displaying section recommendations for a student."""
    try:
        # Get student information
        student_query = """
        FOR student IN users
            FILTER student._id == @student_id AND student.role == "student"
            RETURN {
                "id": student._id,
                "name": student.username,
                "email": student.email
            }
        """
        
        students = list(db.aql.execute(
            student_query,
            bind_vars={"student_id": student_id}
        ))
        
        if not students:
            raise Http404("Student not found")
        
        student = students[0]
        
        # Get section recommendations
        recommended_sections = get_top_sections_for_student(student_id, limit=10)
        
        # Get the student's mistakes
        mistakes_query = """
        FOR edge IN made_mistake
            FILTER edge._from == @student_id AND edge.is_simulated == true
            FOR mistake IN mistakes
                FILTER mistake._id == edge._to
                RETURN {
                    "id": mistake._id,
                    "question": mistake.question,
                    "justification": mistake.justification
                }
        """
        
        student_mistakes = list(db.aql.execute(
            mistakes_query,
            bind_vars={"student_id": student_id}
        ))
        
        # Convert to HTML
        for section in recommended_sections:
            if 'content_preview' in section:
                section['html_preview'] = convert_markdown_to_html(section['content_preview'])
        
        context = {
            'student': student,
            'recommended_sections': recommended_sections,
            'mistakes': student_mistakes,
            'title': f'Recommendations for {student["name"]}'
        }
        
        return render(request, 'network_simulation/student_recommendations.html', context)
    
    except Http404:
        raise
    except Exception as e:
        context = {
            'error': str(e),
            'title': 'Student Recommendations - Error'
        }
        return render(request, 'network_simulation/error.html', context)

@login_required
def instructor_problem_sections(request, instructor_id):
    """View for displaying problematic sections for an instructor."""
    try:
        # Get instructor information
        instructor_query = """
        FOR instructor IN users
            FILTER instructor._id == @instructor_id AND instructor.role == "instructor"
            RETURN {
                "id": instructor._id,
                "name": instructor.username,
                "email": instructor.email
            }
        """
        
        instructors = list(db.aql.execute(
            instructor_query,
            bind_vars={"instructor_id": instructor_id}
        ))
        
        if not instructors:
            raise Http404("Instructor not found")
        
        instructor = instructors[0]
        
        # Get problematic sections
        problem_sections = get_problematic_sections_for_instructor(instructor_id, limit=10)
        
        # Convert to HTML
        for section in problem_sections:
            if 'content_preview' in section:
                section['html_preview'] = convert_markdown_to_html(section['content_preview'])
        
        # Get grading inconsistencies
        inconsistencies_query = """
        FOR course IN courses
            FILTER course.instructor_id == @instructor_id AND course.is_simulated == true
            
            FOR sub1 IN submission
                FILTER sub1.class_code == course.class_code AND sub1.is_simulated == true
                
                FOR sub2 IN submission
                    FILTER sub2.is_simulated == true
                    FILTER sub1._id != sub2._id
                    FILTER sub1.assignment_id == sub2.assignment_id
                    FILTER ABS(sub1.grade - sub2.grade) > 15
                    
                    LET student1 = DOCUMENT(sub1.user_id)
                    LET student2 = DOCUMENT(sub2.user_id)
                    
                    COLLECT 
                        assignment_id = sub1.assignment_id,
                        course_code = course.class_code,
                        course_title = course.class_title
                    AGGREGATE
                        max_diff = MAX(ABS(sub1.grade - sub2.grade)),
                        count = COUNT()
                    
                    FILTER count > 0
                    SORT max_diff DESC
                    LIMIT 5
                    
                    RETURN {
                        "assignment_id": assignment_id,
                        "course": course_title,
                        "course_code": course_code,
                        "max_difference": max_diff,
                        "instance_count": count
                    }
        """
        
        grading_inconsistencies = list(db.aql.execute(
            inconsistencies_query,
            bind_vars={"instructor_id": instructor_id}
        ))
        
        context = {
            'instructor': instructor,
            'problem_sections': problem_sections,
            'inconsistencies': grading_inconsistencies,
            'title': f'Teaching Insights for {instructor["name"]}'
        }
        
        return render(request, 'network_simulation/instructor_problem_sections.html', context)
    
    except Http404:
        raise
    except Exception as e:
        context = {
            'error': str(e),
            'title': 'Instructor Insights - Error'
        }
        return render(request, 'network_simulation/error.html', context)