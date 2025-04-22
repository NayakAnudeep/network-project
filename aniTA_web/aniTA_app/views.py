from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect
from users.arangodb import *
import requests
import io # soon to be unused
import os
import tempfile
import base64

# Create your views here.
def index(request):
    if request.session.get('user_id'):
        role = request.session.get('role')
        if role == 'student':
            return redirect('/dashboard')
        elif role == 'instructor':
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
        courses = db_instructor_courses(user_id)
        # [{'_key': '37712', '_id': 'courses/37712', '_rev': '_jc1X-lu---', 'class_code': 'STPD 6969', 'class_title': 'Intro to Stupidity', 'instructor_id': 'users/36182'},
        #  {'_key': '38591', '_id': 'courses/38591', '_rev': '_jc1757m---', 'class_code': 'WALL-4242', 'class_title': 'Advanced Walls', 'instructor_id': 'users/36182'}]
        context = {}
        context['courses'] = [{'class_code': course['class_code'], 'class_title': course['class_title']} for course in courses]
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
        submissions = db_get_class_assignment_submissions(course_code, assignment_id)
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

        assignment_file = request.FILES.get('assignment_file')
        solution_file = request.FILES.get('solution_file')

        # Convert total_points to integer
        try:
            total_points = int(total_points)
        except (ValueError, TypeError):
            total_points = 100

        err = db_create_assignment(class_code, assignment_name, description, due_date, total_points)
        if err:
            if 'flash_error' not in request.session:
                request.session['flash_error'] = []
            request.session['flash_error'].append(f"Could not add assignment: {err}")
            return redirect('/instructor-dashboard')

        if assignment_file and solution_file:
            assignment_id = db_get_assignment_id(class_code, assignment_name)
            assert assignment_id
            # api_url = "https://ai-context-445405667866.us-central1.run.app/build-context/"
            api_url = "https://ai-vector-search-assessment-445405667866.us-central1.run.app/build-context/"

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

                # Use the files for the API request
                files = {
                    'module_pdf': open(assignment_temp.name, 'rb'),
                    'sample_solution_pdf': open(solution_temp.name, 'rb')
                }

                data = {
                    'class_code': class_code,
                    'assignment_id': assignment_id
                }

                try:
                    # API request
                    response = requests.post(api_url, files=files, data=data)

                    # Process response
                    if response.status_code == 200:
                        api_result = response.json()
                        if api_result.get('status') == 'success':
                            if 'flash_success' not in request.session:
                                request.session['flash_success'] = []
                            request.session['flash_success'].append("Assignment created successfully and context built.")
                        else:
                            if 'flash_error' not in request.session:
                                request.session['flash_error'] = []
                            request.session['flash_error'].append(f"Created assignment but failed to build context: {api_result.get('message')}")
                    else:
                        if 'flash_error' not in request.session:
                            request.session['flash_error'] = []
                        request.session['flash_error'].append(f"Created assignment but failed to build context: API returned status {response.status_code}")
                finally:
                    # Close the file handlers opened for the request
                    for f in files.values():
                        f.close()

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

        # TODO ping API to prompt grading
        # TODO modify html to preview previous submission (iframe thing, I think)

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

        return HttpResponse(template.render(context, request))

    else:
        return redirect('/')

def view_pdf(request, submission_id):
    # Get submission from DB
    submission = db_get_submission_by_id(submission_id)
    if not submission:
        return HttpResponse("PDF not found", status=404)

    # Decode the PDF from base64
    pdf_data = base64.b64decode(submission.get("file_content"))
    print(f"PDF data length: {len(pdf_data) if pdf_data else 'None'}")
    if not pdf_data:
        return HttpResponse("PDF data not found", status=404)

    # Decode the PDF from base64
    try:
        # # Debug: Write the PDF to a file to check its contents
        # import os
        # debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_pdfs')
        # os.makedirs(debug_dir, exist_ok=True)
        # debug_file_path = os.path.join(debug_dir, f'submission_{submission_id}.pdf')

        # with open(debug_file_path, 'wb') as f:
        #     f.write(pdf_data)
        # print(f"Debug PDF written to: {debug_file_path}")

        # Return the PDF with proper content type
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Content-Disposition'] = 'inline; filename="document.pdf"'
        response
        return response
    except TypeError:
        return HttpResponse("Invalid PDF data", status=500)
