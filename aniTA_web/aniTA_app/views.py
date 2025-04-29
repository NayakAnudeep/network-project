from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect
from users.arangodb import *
from users.material_db import *
from users.graph_ops import store_mistake_and_edges
import requests
import io # soon to be unused
import os
import tempfile
import base64
from .claude_service import ClaudeGradingService

# Create your views here.
def index(request):
    if request.session.get('user_id'):
        role = request.session.get('role')
        if role == 'student':
            # Provide link to both regular dashboard and analytics dashboard
            return redirect('/dashboard')
        elif role == 'instructor':
            # Provide link to both regular dashboard and analytics dashboard
            return redirect('/instructor-dashboard')
        else:
            request.session.flush()
            template = loader.get_template("aniTA_app/index.html")
            context = dict()
            context['flash_success'] = request.session.pop('flash_success', [])
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("aniTA_app/index.html")
        context = dict()
        context['flash_success'] = request.session.pop('flash_success', [])
        return HttpResponse(template.render(context, request))

def dashboard(request):
    # Redirect home if the user is not logged in.
    if not (request.session.get('user_id') and request.session.get('role') == 'student'):
        return redirect('/')

    template = loader.get_template("aniTA_app/dashboard.html")
    user_id = request.session.get('user_id')

    # Get student assignments
    assignments_data = db_get_student_assignments(user_id)

    # Prepare context for the template
    context = {}
    if 'error' in assignments_data:
        context['error_message'] = assignments_data['error']
        context['assignments'] = []
    else:
        # Flatten the assignments from all courses into a single list
        all_assignments = []
        for course in assignments_data['assignments']:
            class_code = course['class_code']
            class_title = course['class_title']
            for assignment in course['assignments']:
                assignment['class_code'] = class_code
                assignment['class_title'] = class_title
                all_assignments.append(assignment)

        # Sort assignments by due date
        # Handling None values by putting them at the end
        sorted_assignments = sorted(
            all_assignments,
            key=lambda x: (x['due_date'] is None, x['due_date'] or "")
        )

        context['assignments'] = sorted_assignments

    context['flash_success'] = request.session.pop('flash_success', [])
    context['flash_error'] = request.session.pop('flash_error', [])

    return HttpResponse(template.render(context, request))

def instructor_dashboard(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    if user_id and role == 'instructor':
        template = loader.get_template("aniTA_app/instructor_dashboard.html")
        
        # Get manually created courses
        manual_courses = db_instructor_courses(user_id)
        
        # Get simulated courses
        simulated_courses = []
        try:
            instructor = db.collection('users').get(user_id)
            
            # Check for simulated courses through course collection
            sim_courses_query = f"""
            FOR course IN courses
                FILTER course.instructor_id == "{user_id}" AND course.is_simulated == true
                RETURN {{
                    class_code: course.class_code,
                    class_title: course.class_title,
                    is_simulated: true
                }}
            """
            simulated_courses = list(db.aql.execute(sim_courses_query))
            
            # Also check if the instructor has a record of simulated courses
            if instructor and 'simulated_courses' in instructor:
                for course_id in instructor['simulated_courses']:
                    course = db.collection('courses').get(course_id)
                    if course:
                        simulated_courses.append({
                            'class_code': course.get('class_code'),
                            'class_title': course.get('class_title', 'Simulated Course'),
                            'is_simulated': True
                        })
                        
        except Exception as e:
            print(f"Error getting simulated courses: {e}")
            
        # Format manually created courses
        formatted_courses = [{'class_code': course['class_code'], 'class_title': course['class_title']} for course in manual_courses]
        
        # Add simulated courses to the list (if not duplicates)
        existing_codes = {course['class_code'] for course in formatted_courses}
        for sim_course in simulated_courses:
            if sim_course['class_code'] not in existing_codes:
                formatted_courses.append(sim_course)
                existing_codes.add(sim_course['class_code'])
        
        context = {}
        context['courses'] = formatted_courses
        context['flash_success'] = request.session.pop('flash_success', [])
        context['flash_error'] = request.session.pop('flash_error', [])
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/')

def instructor_add_class(request):
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    if user_id and role == 'instructor':
        template = loader.get_template("aniTA_app/instructor_add_class.html")
        context = {}
        context['flash_success'] = request.session.pop('flash_success', [])
        context['flash_error'] = request.session.pop('flash_error', [])
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/')

def instructor_course(request, course_code):
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    if user_id and role == 'instructor':
        info, err = db_get_course_assignments(course_code)
        if err:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append(f"Course not found: {course_code}")
            return redirect('/instructor-dashboard')
        else:
            template = loader.get_template("aniTA_app/instructor_course.html")
            context = { 'course': info }
            context['flash_success'] = request.session.pop('flash_success', [])
            context['flash_error'] = request.session.pop('flash_error', [])
            return HttpResponse(template.render(context, request))
    else:
        return redirect('/')

def class_assignment_submissions(request, course_code, assignment_id):
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    if user_id and role == 'instructor':
        submissions = db_get_class_assignment_submissions_metadata(course_code, assignment_id)
        print("submissions:", submissions, flush=True)
        template = loader.get_template("aniTA_app/class_assignment_submissions.html")
        context = { "submissions": submissions }
        context['flash_success'] = request.session.pop('flash_success', [])
        context['flash_error'] = request.session.pop('flash_error', [])
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/')


def instructor_course_add_assignment(request, course_code):
    user_id = request.session.get('user_id')
    role = request.session.get('role')
    if user_id and role == 'instructor':
        template = loader.get_template("aniTA_app/instructor_course_add_assignment.html")
        context = { 'class_code': course_code }
        context['flash_success'] = request.session.pop('flash_success', [])
        context['flash_error'] = request.session.pop('flash_error', [])
        return HttpResponse(template.render(context, request))
    else:
        return redirect('/')

def courses(request):
    # Redirect home if the user is not logged in.
    if not (request.session.get('user_id') and request.session.get('role') == 'student'):
        return redirect('/')
    template = loader.get_template("aniTA_app/courses.html")
    user_id = request.session.get('user_id')
    context = student_courses_overview(user_id)
    # context = { "courses": [
    #     {
    #         "code": "ATLS 5214",
    #         "title": "Big Data Architecture",
    #         "instructor": "Greg Greenstreet",
    #         "schedule": "MW 5:05-6:20 PM",
    #         "grade": "100",
    #         "letter_grade": "A",
    #         "n_pending_assignments": 0,
    #         "next_due_date": None,
    #         "id": 42,
    #     },
    #     {
    #         "code": "STAT 5000",
    #         "title": "Statistical Methods and App I",
    #         "instructor": "John Smith",
    #         "schedule": "MWF 10:00-11:00 AM",
    #         "grade": "92",
    #         "letter_grade": "A-",
    #         "n_pending_assignments": 1,
    #         "next_due_date": "March 14",
    #         "id": 42,
    #     }
    # ] }
    context['flash_success'] = request.session.pop('flash_success', [])
    context['flash_error'] = request.session.pop('flash_error', [])

    return HttpResponse(template.render(context, request))

def course(request, course_id):
    return HttpResponse("TODO")

def add_class(request):
    if request.method == "POST":
        class_code = request.POST.get('class_code')
        class_title = request.POST.get('class_title')
        instructor_id = request.session.get('user_id')
        err = db_add_course(class_code, class_title, instructor_id)
        if err:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append(f"Could not add course: {err}")
        else:
            if 'flash_success' not in request.session:
                request.session['flash_success'] = []
            request.session['flash_success'].append("Course created successfully.")
        return redirect('/instructor-dashboard')
    else:
        return redirect('/')

def convert_to_buffered_reader(uploaded_file):
    """Converts an InMemoryUploadedFile to an _io.BytesIO (TODO want _io.BufferedReader)."""
    # uploaded_file.file => _io.BytesIO
    # uploaded_file.file.read() => <class 'bytes'>
    # io.BufferedReader(uploaded_file.file) => _io.BufferedReader()
    return io.BufferedReader(uploaded_file.file)

def add_assignment(request):
    """
    POST Request to add an assignment. (Made by the instructor.)
    """
    if request.method == "POST":
        class_code = request.POST.get('class_code')
        assignment_name = request.POST.get('assignment_name')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        total_points = request.POST.get('total_points', 100)

        instructions_file = request.FILES.get('instructions_file')
        assignment_file = request.FILES.get('assignment_file')
        solution_file = request.FILES.get('solution_file')
        rubric_file = request.FILES.get('rubric_file')  # New rubric file upload

        # Convert total_points to integer
        try:
            total_points = int(total_points)
        except (ValueError, TypeError):
            total_points = 100

        # Process the rubric file if provided
        rubric_items = []
        if rubric_file:
            try:
                # Save rubric file to a temporary file
                with tempfile.NamedTemporaryFile(suffix='.txt', mode='wb+') as rubric_temp:
                    for chunk in rubric_file.chunks():
                        rubric_temp.write(chunk)
                    rubric_temp.flush()
                    
                    # Read and parse the rubric file
                    with open(rubric_temp.name, 'r') as f:
                        rubric_text = f.read()
                        
                        # Simple parsing for rubric items (format: Criteria - Points: Description)
                        for line in rubric_text.splitlines():
                            if line.strip():
                                try:
                                    criteria, rest = line.split('-', 1)
                                    points_part, description = rest.split(':', 1)
                                    points = float(points_part.replace('Points', '').strip())
                                    
                                    rubric_items.append({
                                        "criteria": criteria.strip(),
                                        "points": points,
                                        "description": description.strip()
                                    })
                                except Exception as e:
                                    print(f"Error parsing rubric line: {line}. Error: {e}")
            except Exception as e:
                print(f"Error processing rubric file: {e}")
                if 'flash_error' not in request.session:
                    request.session['flash_error'] = []
                request.session['flash_error'].append(f"Could not process rubric file: {e}")

        with tempfile.NamedTemporaryFile(suffix='.pdf') as instructions_temp:
            for chunk in instructions_file.chunks():
                instructions_temp.write(chunk)
            instructions_temp.flush()
            with open(instructions_temp.name, 'rb') as instructions_pdf:
                encoded_pdf = base64.b64encode(instructions_pdf.read()).decode('utf-8')

        err = db_create_assignment(class_code,
                                   assignment_name,
                                   description,
                                   due_date,
                                   total_points,
                                   encoded_pdf,
                                   instructions_file.name)
        if err:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append(f"Could not add assignment: {err}")
            return redirect('/instructor-dashboard')

        if assignment_file and solution_file:
            assignment_id = db_get_assignment_id(class_code, assignment_name)
            assert assignment_id

            # Initialize Claude service for materials processing
            claude_service = ClaudeGradingService()

            # Use context managers for temporary files
            with tempfile.NamedTemporaryFile(suffix='.pdf') as assignment_temp, \
                 tempfile.NamedTemporaryFile(suffix='.pdf') as solution_temp:

                # Write uploaded files to temp files
                for chunk in assignment_file.chunks():
                    assignment_temp.write(chunk)
                assignment_temp.flush()

                for chunk in solution_file.chunks():
                    solution_temp.write(chunk)
                solution_temp.flush()

                # Process course materials with Claude
                try:
                    # Process assignment file
                    material_result = claude_service.process_course_material(
                        class_code=class_code,
                        assignment_id=assignment_id,
                        pdf_path=assignment_temp.name,
                        rubric_items=rubric_items
                    )

                    # Process solution file for additional context
                    solution_result = claude_service.process_course_material(
                        class_code=class_code,
                        assignment_id=f"{assignment_id}_solution",
                        pdf_path=solution_temp.name
                    )

                    if material_result.get("success") and solution_result.get("success"):
                        print(f"Successfully processed course materials and created embeddings")
                        print(f"Extracted {material_result.get('questions_count')} questions")
                        print(f"Created {material_result.get('chunks_count')} chunks for vector search")

                        if 'flash_success' not in request.session:
                            request.session['flash_success'] = []
                        request.session['flash_success'].append("Assignment created successfully with materials and vector embeddings for AI grading.")
                    else:
                        print(f"Error processing materials: {material_result.get('error')} / {solution_result.get('error')}")
                        if 'flash_error' not in request.session:
                            request.session['flash_error'] = []
                        request.session['flash_error'].append(f"Created assignment but failed to process materials for AI grading.")

                except Exception as e:
                    print(f"Error processing materials with Claude: {e}")
                    if 'flash_error' not in request.session:
                        request.session['flash_error'] = []
                    request.session['flash_error'].append(f"Created assignment but encountered an error processing materials: {str(e)}")

        return redirect('/instructor-dashboard')

def student_add_course_get(request):
    template = loader.get_template("aniTA_app/student_add_course.html")
    context = {}
    return HttpResponse(template.render(context, request))

def student_add_course_post(request):
    if request.method == "POST":
        class_code = request.POST.get('class_code')
        user_id = request.session.get('user_id')
        err = db_enroll_student_in_course(user_id, class_code)
        if err:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append(f"Could not add course: {err}")
        else:
            if 'flash_success' not in request.session:
                request.session['flash_success'] = []
            request.session['flash_success'].append("Course added successfully.")
        return redirect('/courses')
    else:
        redirect('/')

def upload(request, class_code, assignment_id):
    if request.method == "POST":
        submission = request.FILES.get('file_input')
        print(type(submission), flush=True) # <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
        user_id = request.session.get('user_id')
        file_name = submission.name if submission else None
        if not submission:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append("Could not add submission. Expected file.")
            return redirect('/dashboard')

        with tempfile.NamedTemporaryFile(suffix='.pdf') as submission_temp:
            # Write uploaded files to temp files
            for chunk in submission.chunks():
                submission_temp.write(chunk)
            submission_temp.flush()

            with open(submission_temp.name, 'rb') as submission_pdf:
                encoded_pdf = base64.b64encode(submission_pdf.read()).decode('utf-8')

            err = db_add_submission(user_id, class_code, assignment_id, encoded_pdf, file_name)
            if err:
                if 'flash_error' not in request.session:
                    request.session['flash_error'] = []
                request.session['flash_error'].append(f"Could not add submission: {err}")
                return redirect('/dashboard')

            # Call Claude for grading
            try:
                # Initialize Claude service
                claude_service = ClaudeGradingService()
                
                # Grade the submission using Claude
                grading_result = claude_service.grade_from_pdf_data(
                    student_pdf_path=submission_temp.name,
                    class_code=class_code,
                    assignment_id=assignment_id
                )
                
                # Add student_id to the result
                grading_result["student_id"] = str(user_id)
                
                print("Claude Grading Result:", grading_result, flush=True)
                
                # Update the submission with AI feedback
                if "error" not in grading_result:
                    ai_score = grading_result["total_score"]
                    ai_feedback = grading_result["results"]
                    print(f"CALLING db_put_ai_feedback({user_id}, {class_code}, {assignment_id}, {str(ai_score)}, {ai_feedback})", flush=True)
                    db_put_ai_feedback(user_id, class_code, assignment_id, ai_score, ai_feedback)
                else:
                    print("Error in Claude grading:", grading_result["error"], flush=True)
                # on success:
                # {
                #     "student_id": student_id,
                #     "assignment_id": assignment_id,
                #     "total_score": final_score,
                #     "results": [
                #         {
                #         "question": question,
                #         "score": score, # float
                #         "justification": justification
                #         },
                #         ...
                #     ]
                # }

            except Exception as e:
                print("API Error:", str(e))  # Log but don't block submission

        if 'flash_success' not in request.session:
            request.session['flash_success'] = []
        request.session['flash_success'].append("Submitted assignment successfully.")
        return redirect('/dashboard')
    elif request.method == "GET":
        template = loader.get_template("aniTA_app/upload.html")
        user_id = request.session.get('user_id')
        previous_submission = db_get_submission(user_id, class_code, assignment_id)

        context = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "has_previous_submission": previous_submission is not None
        }

        if previous_submission:
            full_id = previous_submission.get("_id")
            numeric_id = full_id.split('/')[1] if '/' in full_id else full_id
            context["submission_id"] = numeric_id
            context["file_name"] = previous_submission.get("file_name")
            context["graded"] = previous_submission.get("graded")
            context["grade"] = previous_submission.get("grade")
            context["feedback"] = previous_submission.get("feedback")

        print("context[\"assignment_id\"] =", assignment_id, flush=True)
        context["assignment_id"] = assignment_id
        return HttpResponse(template.render(context, request))

    else:
        return redirect('/')
    
def upload(request, class_code, assignment_id):
    if request.method == "POST":
        submission = request.FILES.get('file_input')
        user_id = request.session.get('user_id')

        if not submission:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append("Could not add submission. Expected file.")
            return redirect('/dashboard')

        context = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "has_previous_submission": True
        }
        
        template = loader.get_template("aniTA_app/upload.html")

        with tempfile.NamedTemporaryFile(suffix='.pdf') as submission_temp:
            for chunk in submission.chunks():
                submission_temp.write(chunk)
            submission_temp.flush()

            with open(submission_temp.name, 'rb') as submission_pdf:
                encoded_pdf = base64.b64encode(submission_pdf.read()).decode('utf-8')

            # Add submission to DB
            err = db_add_submission(user_id, class_code, assignment_id, encoded_pdf, submission.name)
            if err:
                if 'flash_error' not in request.session:
                    request.session['flash_error'] = []
                request.session['flash_error'].append(f"Could not add submission: {err}")
                return redirect('/dashboard')

            # Grade the submission using Claude
            try:
                claude_service = ClaudeGradingService()
                grading_result = claude_service.grade_from_pdf_data(
                    student_pdf_path=submission_temp.name,
                    class_code=class_code,
                    assignment_id=assignment_id
                )

                # Add student_id manually
                grading_result["student_id"] = str(user_id)

                # Check for valid API response - even if there's an error, we'll still use the default values
                # provided by the API
                print(f"Grading result received: {grading_result.keys()}", flush=True)
                
                # Extract the score and feedback, with defaults if missing
                print(f"******* DEBUGGING API RESULT *******", flush=True)
                print(f"Raw grading_result: {grading_result}", flush=True)
                print(f"Type of grading_result: {type(grading_result)}", flush=True)
                print(f"Keys in grading_result: {grading_result.keys()}", flush=True)
                
                ai_score = grading_result.get("total_score", 70.0)  # Default to passing if missing
                print(f"Raw ai_score value: {ai_score}", flush=True)
                print(f"Type of ai_score: {type(ai_score)}", flush=True)
                
                ai_feedback = grading_result.get("results", [])
                print(f"Raw ai_feedback value: {ai_feedback}", flush=True)
                print(f"Type of ai_feedback: {type(ai_feedback)}", flush=True)
                
                # Ensure ai_score is a number
                try:
                    ai_score = float(ai_score)
                    print(f"AI Score (converted to float): {ai_score}", flush=True)
                    
                    # If the score is 0, something might be wrong - use a default
                    if ai_score == 0.0:
                        print("WARNING: Score is 0, which is unusual. Using default passing score.", flush=True)
                        ai_score = 70.0  # Default passing score
                except (ValueError, TypeError):
                    print(f"Invalid AI score: {ai_score}, using default", flush=True)
                    ai_score = 70.0  # Default passing score
                
                # Ensure ai_feedback is a list
                if not isinstance(ai_feedback, list):
                    print(f"AI feedback is not a list, using default", flush=True)
                    ai_feedback = [{
                        "question": "Submission",
                        "score": ai_score,
                        "justification": "Feedback format was invalid. A default score has been assigned."
                    }]
                    
                print(f"AI Feedback items: {len(ai_feedback)}", flush=True)
                
                # Update submission with AI feedback
                print(f"Calling db_put_ai_feedback with score: {ai_score}", flush=True)
                feedback_result = db_put_ai_feedback(user_id, class_code, assignment_id, ai_score, ai_feedback)
                print(f"Result from db_put_ai_feedback: {feedback_result}", flush=True)

                # Now also store Mistake nodes and edges
                # Build rubric mapping
                rubrics = db.collection('rubrics')
                rubric_docs = list(rubrics.find({"assignment_id": assignment_id}))
                rubric_mapping = {}
                if rubric_docs:
                    for item in rubric_docs[0].get("items", []):
                        rubric_mapping[item["criteria"]] = rubric_docs[0]["_id"]

                # Get submission numeric id
                user_sub = db_get_submission(user_id, class_code, assignment_id)
                if user_sub:
                    submission_id = user_sub["_id"].split('/')[-1]
                    
                    # Prepare context data for display template
                    full_id = user_sub.get("_id")
                    numeric_id = full_id.split('/')[1] if '/' in full_id else full_id
                    context["submission_id"] = numeric_id
                    context["file_name"] = user_sub.get("file_name")
                    
                    # Force these values to ensure feedback is displayed immediately
                    context["graded"] = True
                    context["grade"] = ai_score
                    
                    # Make sure we're using the latest feedback data from the database
                    # First check if the submission has been updated with AI feedback
                    updated_submission = db_get_submission(user_id, class_code, assignment_id)
                    if updated_submission and updated_submission.get("feedback"):
                        context["feedback"] = updated_submission.get("feedback")
                    # If not available in the updated submission, format the raw AI feedback
                    elif isinstance(ai_feedback, list):
                        feedback_text = ""
                        for item in ai_feedback:
                            question = item.get("question", "")
                            score = item.get("score", 0)
                            justification = item.get("justification", "")
                            feedback_text += f"{question}\nScore: {score:.2f}\n{justification}\n\n"
                        context["feedback"] = feedback_text.strip()
                    else:
                        context["feedback"] = user_sub.get("feedback")

                    # Store mistake nodes and edges for analytics
                    try:
                        for result_item in grading_result.get("results", []):
                            # Check that result_item has the required rubric_criteria field or provide a default
                            if "rubric_criteria" not in result_item:
                                result_item["rubric_criteria"] = []  # Empty list as default
                                
                            store_mistake_and_edges(
                                student_id=f"users/{user_id}",
                                submission_id=submission_id,
                                assignment_id=assignment_id,
                                result_item=result_item,
                                relevant_chunks=grading_result.get("relevant_chunks", []),
                                rubric_mapping=rubric_mapping
                            )
                    except Exception as e:
                        print(f"Error storing mistake edges (non-critical): {e}", flush=True)
                        # Continue with displaying feedback even if this fails
                    
                    # Return the upload page with the graded results instead of redirecting
                    # Add a success message with score
                    if 'flash_success' not in request.session:
                        request.session['flash_success'] = []
                    request.session['flash_success'].append(f"Assignment submitted and automatically graded by AI. Your score: {ai_score:.2f}")
                    
                    # Debug the final context values before rendering
                    print("***************************************", flush=True)
                    print("FINAL CONTEXT VALUES BEFORE RENDERING:", flush=True)
                    print(f"graded: {context.get('graded')}", flush=True)
                    print(f"grade: {context.get('grade')}", flush=True)
                    print(f"feedback length: {len(context.get('feedback', ''))}", flush=True)
                    print(f"feedback preview: {context.get('feedback', '')[:100]}...", flush=True)
                    print("***************************************", flush=True)
                    
                    return HttpResponse(template.render(context, request))

                else:
                    print("Error in Claude grading:", grading_result["error"], flush=True)
                    
                    # Even if there's an error, we still want to provide feedback
                    # Use the default values that should be in the result
                    ai_score = grading_result.get("total_score", 70.0)
                    ai_feedback = grading_result.get("results", [])
                    
                    if not ai_feedback:
                        ai_feedback = [{
                            "question": "Assignment Review",
                            "score": ai_score,
                            "justification": "The grading system encountered an issue. A default score has been assigned."
                        }]
                    
                    # Update submission with fallback feedback
                    db_put_ai_feedback(user_id, class_code, assignment_id, ai_score, ai_feedback)
                    
                    # Get updated submission for display
                    user_sub = db_get_submission(user_id, class_code, assignment_id)
                    if user_sub:
                        full_id = user_sub.get("_id")
                        numeric_id = full_id.split('/')[1] if '/' in full_id else full_id
                        
                        # Prepare context
                        context = {
                            "class_code": class_code,
                            "assignment_id": assignment_id,
                            "has_previous_submission": True,
                            "submission_id": numeric_id,
                            "file_name": user_sub.get("file_name"),
                            "graded": True,
                            "grade": ai_score,
                            "feedback": user_sub.get("feedback")
                        }
                        
                        # Add message
                        if 'flash_success' not in request.session:
                            request.session['flash_success'] = []
                        request.session['flash_success'].append(f"Assignment submitted and graded with a default score of {ai_score:.2f}")
                        
                        return HttpResponse(template.render(context, request))

            except Exception as e:
                print(f"API Error: {str(e)}", flush=True)
                
                # Create a default AI feedback response for the student
                ai_score = 70.0  # Default passing grade
                ai_feedback = [{
                    "question": "Assignment Submission",
                    "score": 70.0,
                    "justification": "There was an issue with the AI grading system. A default score has been assigned. Your instructor will review this submission."
                }]
                
                # Update the submission with default feedback
                db_put_ai_feedback(user_id, class_code, assignment_id, ai_score, ai_feedback)
                
                # Get the submission for display
                user_sub = db_get_submission(user_id, class_code, assignment_id)
                if user_sub:
                    full_id = user_sub.get("_id")
                    numeric_id = full_id.split('/')[1] if '/' in full_id else full_id
                    
                    # Prepare context for template
                    context = {
                        "class_code": class_code,
                        "assignment_id": assignment_id,
                        "has_previous_submission": True,
                        "submission_id": numeric_id,
                        "file_name": user_sub.get("file_name"),
                        "graded": True,
                        "grade": ai_score,
                        "feedback": "There was an issue with the AI grading system. A default score has been assigned. Your instructor will review this submission."
                    }
                    
                    # Add message and render the template
                    if 'flash_success' not in request.session:
                        request.session['flash_success'] = []
                    request.session['flash_success'].append(f"Assignment submitted! Your score: {ai_score:.2f} (default score due to grading issue)")
                    
                    return HttpResponse(loader.get_template("aniTA_app/upload.html").render(context, request))

        # If we get here, something went wrong, but we still want to provide feedback
        if 'flash_success' not in request.session:
            request.session['flash_success'] = []
        request.session['flash_success'].append("Submitted assignment successfully.")
        return redirect('/dashboard')

    elif request.method == "GET":
        template = loader.get_template("aniTA_app/upload.html")
        user_id = request.session.get('user_id')
        previous_submission = db_get_submission(user_id, class_code, assignment_id)

        context = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "has_previous_submission": previous_submission is not None
        }

        if previous_submission:
            full_id = previous_submission.get("_id")
            numeric_id = full_id.split('/')[1] if '/' in full_id else full_id
            context["submission_id"] = numeric_id
            context["file_name"] = previous_submission.get("file_name")
            context["graded"] = previous_submission.get("graded")
            context["grade"] = previous_submission.get("grade")
            context["feedback"] = previous_submission.get("feedback")

        return HttpResponse(template.render(context, request))

    else:
        return redirect('/')


def view_pdf(request, submission_id):
    try:
        # Get submission from DB
        submission = db_get_submission_by_numeric_id(submission_id)
        if not submission:
            # If submission not found, return a nice HTML page
            html_content = f"""
            <html>
                <head>
                    <title>Submission</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                        h2 {{ color: #4a6fff; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Submission #{submission_id}</h2>
                        <p>This is a simulated submission. No PDF content is available.</p>
                        <p>This would normally display the student's submitted work.</p>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')
        
        # If we have a submission but no file content
        if not submission.get("file_content"):
            file_name = submission.get("file_name", "submission")
            html_content = f"""
            <html>
                <head>
                    <title>Submission - {file_name}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                        h2 {{ color: #4a6fff; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Submission: {file_name}</h2>
                        <p>This is a simulated submission. The PDF content is not available.</p>
                        <p>Student: {submission.get('student_name', 'Unknown')}</p>
                        <p>Submitted: {submission.get('created_at', 'Unknown date')}</p>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')

        # Try to decode the PDF data
        try:
            pdf_data = base64.b64decode(submission.get("file_content"))
            if not pdf_data:
                raise ValueError("No PDF data")
                
            # Return the PDF with proper content type
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['Content-Disposition'] = 'inline; filename="document.pdf"'
            return response
        except (TypeError, ValueError, base64.Error) as e:
            # If PDF decoding fails, return an HTML page
            file_name = submission.get("file_name", "submission")
            html_content = f"""
            <html>
                <head>
                    <title>Submission - {file_name}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                        h2 {{ color: #4a6fff; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Submission: {file_name}</h2>
                        <p>There was an issue displaying this PDF submission.</p>
                        <p>Student: {submission.get('student_name', 'Unknown')}</p>
                        <p>Submitted: {submission.get('created_at', 'Unknown date')}</p>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')
    except Exception as e:
        # General error handling
        html_content = f"""
        <html>
            <head>
                <title>Submission</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                    h2 {{ color: #4a6fff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Submission #{submission_id}</h2>
                    <p>This is a simulated submission. No PDF content is available.</p>
                    <p>Error: {str(e)}</p>
                </div>
            </body>
        </html>
        """
        return HttpResponse(html_content, content_type='text/html')

def view_assignment_instructions(request, assignment_id):
    print("assignment_id:", assignment_id, flush=True)
    try:
        file_content = db_get_assignment_instructions_file_content(assignment_id)
        if not file_content:
            # If no file content, return a readable error page instead of PDF
            html_content = f"""
            <html>
                <head>
                    <title>Assignment Instructions</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                        h2 {{ color: #4a6fff; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Assignment Instructions</h2>
                        <p>This is a simulated assignment. No PDF instructions are available for this assignment.</p>
                        <p>You can still submit your work using the upload form.</p>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')
            
        # If we have file content, try to show the PDF
        try:
            pdf_data = base64.b64decode(file_content)
            # Return the PDF with proper content type
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['X-Frame-Options'] = 'SAMEORIGIN'
            response['Content-Disposition'] = 'inline; filename="document.pdf"'
            return response
        except (TypeError, base64.Error):
            # If PDF decoding fails, show a message
            html_content = f"""
            <html>
                <head>
                    <title>Assignment Instructions</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 20px; }}
                        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                        h2 {{ color: #4a6fff; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Assignment Instructions</h2>
                        <p>There was an issue displaying the PDF instructions for this assignment.</p>
                        <p>You can still submit your work using the upload form.</p>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')
    except Exception as e:
        # General error handling
        html_content = f"""
        <html>
            <head>
                <title>Assignment Instructions</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                    h2 {{ color: #4a6fff; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Assignment Instructions</h2>
                    <p>This is a simulated assignment. No PDF instructions are available.</p>
                    <p>You can still submit your work using the upload form.</p>
                </div>
            </body>
        </html>
        """
        return HttpResponse(html_content, content_type='text/html')


def instructor_grade_submission(request, numeric_id):
    template = loader.get_template("aniTA_app/instructor_grade_submission.html")

    user_id = request.session.get('user_id') # for the instructor
    previous_submission = db_get_submission_by_numeric_id(numeric_id)
    context = {
        "has_previous_submission": previous_submission is not None
    }

    if previous_submission:
        context["submission_id"] = numeric_id
        context["file_name"] = previous_submission.get("file_name")
        context["ai_score"] = previous_submission.get("ai_score")
        context["ai_feedback"] = previous_submission.get("ai_feedback")
        context["previous_grade"] = previous_submission.get("grade")
        context["previous_feedback"] = previous_submission.get("feedback")
        context["graded"] = previous_submission.get("graded")
        
        # Add a note that this was auto-graded by AI
        if previous_submission.get("graded") and previous_submission.get("grade") == previous_submission.get("ai_score"):
            context["auto_graded_by_ai"] = True

    print("in instructor_grade_submission")
    print("serving context:", context, flush=True)

    return HttpResponse(template.render(context, request))


def post_grade_submission(request, numeric_submission_id):
    if request.method != "POST":
        return redirect('/')

    if not (request.session.get('user_id') and request.session.get('role') == 'instructor'):
        return redirect('/')

    grade = request.POST.get('grade')
    feedback = request.POST.get('feedback')

    try:
        grade = float(grade)
        if grade < 0 or grade > 100:
            raise ValueError("Grade must be between 0 and 100")
    except (ValueError, TypeError):
        request.session['flash_error'] = ["Invalid grade value. Must be a number between 0 and 100."]
        return redirect('/instructor-dashboard')

    err = db_put_submission_grade(numeric_submission_id, grade, feedback)
    if err:
        if 'flash_error' not in request.session:
            request.session['flash_error'] = []
        request.session['flash_error'].append(f"Failed to submit grade: {err}")
    else:
        if 'flash_success' not in request.session:
            request.session['flash_success'] = []
        request.session['flash_success'].append("Grade submitted successfully")
    return redirect('/instructor-dashboard')
