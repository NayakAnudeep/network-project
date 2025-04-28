"""
Test script for Claude API integration with vector search and rubrics

This script tests the Claude API integration in the AniTA project.
Make sure to set the ANTHROPIC_API_KEY environment variable before running this script.

Usage:
    python test_claude_integration.py

"""

import os
import sys
import django
import tempfile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aniTA_server.settings')
django.setup()

from django.conf import settings
from aniTA_app.claude_service import ClaudeGradingService
from users.material_db import (
    store_course_material,
    store_rubric,
    get_rubric
)

def main():
    # Check if API key is set
    if not settings.ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY is not set in settings or environment variables.")
        print("Set the environment variable with:")
        print("    export ANTHROPIC_API_KEY=your_api_key_here")
        return 1
    
    print(f"Using Anthropic API key: {settings.ANTHROPIC_API_KEY[:5]}...")
    
    # Create sample materials
    test_material = """
    # Sample Course Material
    
    ## Introduction to Programming
    
    This material covers the basics of programming concepts.
    
    Q1: What is a variable?
    A variable is a named storage location in computer memory that can hold a value.
    
    Q2: Explain the difference between a compiler and an interpreter.
    A compiler translates the entire program into machine code before execution, while an interpreter executes the program line by line.
    """
    
    test_rubric = [
        {
            "criteria": "Correctness",
            "points": 5.0,
            "description": "The answer must be factually correct and address all parts of the question."
        },
        {
            "criteria": "Completeness",
            "points": 3.0,
            "description": "The answer must cover all aspects of the question in sufficient detail."
        },
        {
            "criteria": "Clarity",
            "points": 2.0,
            "description": "The answer must be clear, well-organized, and easy to understand."
        }
    ]
    
    # Create a sample student submission
    test_student_answer = """
    # Student Submission
    
    Q1: What is a variable?
    A variable is a place in computer memory where we can store information that can be changed.
    
    Q2: Explain the difference between a compiler and an interpreter.
    A compiler converts code to machine language all at once, while an interpreter goes through the code line by line.
    """
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w+') as material_file, \
         tempfile.NamedTemporaryFile(suffix='.txt', mode='w+') as student_file:
        
        # Write content to files
        material_file.write(test_material)
        material_file.flush()
        
        student_file.write(test_student_answer)
        student_file.flush()
        
        print("\nTesting Claude grading with vector search and rubrics...")
        
        try:
            # Initialize Claude service
            claude_service = ClaudeGradingService()
            print("Claude service initialized successfully!")
            
            # Test course material processing
            class_code = "TEST101"
            assignment_id = "TEST101_0"
            
            print("\nProcessing course material...")
            material_result = claude_service.process_course_material(
                class_code=class_code,
                assignment_id=assignment_id,
                pdf_path=material_file.name,
                rubric_items=test_rubric
            )
            
            if material_result.get("success"):
                print(f"Successfully processed course material:")
                print(f"- Material ID: {material_result.get('material_id')}")
                print(f"- Questions extracted: {material_result.get('questions_count')}")
                print(f"- Chunks created: {material_result.get('chunks_count')}")
            else:
                print(f"Error processing course material: {material_result.get('error')}")
                return 1
            
            # Verify rubric was saved
            print("\nVerifying rubric storage...")
            rubric = get_rubric(class_code, assignment_id)
            if rubric and len(rubric.get("items", [])) == len(test_rubric):
                print(f"Successfully stored rubric with {len(rubric.get('items', []))} criteria")
            else:
                print("Error: Rubric not found or incomplete")
                
            # Test grading
            print("\nTesting grading with vector search...")
            grading_result = claude_service.grade_from_pdf_data(
                student_pdf_path=student_file.name,
                class_code=class_code,
                assignment_id=assignment_id
            )
            
            print("\nGrading Results:")
            print(f"Total score: {grading_result.get('total_score', 'N/A')}")
            
            for item in grading_result.get('results', []):
                print(f"\nQuestion: {item.get('question', 'Unknown')}")
                print(f"Score: {item.get('score', 'N/A')}")
                print(f"Feedback: {item.get('justification', 'N/A')[:100]}...")
                
                # Check if rubric criteria were used
                if "rubric_criteria" in item:
                    print("Rubric criteria feedback:")
                    for criteria in item.get("rubric_criteria", []):
                        print(f"- {criteria.get('criteria')}: {criteria.get('points')} points")
                        print(f"  {criteria.get('feedback')[:50]}...")
            
            print("\nTest completed successfully!")
            return 0
        except Exception as e:
            print(f"Error during test: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
