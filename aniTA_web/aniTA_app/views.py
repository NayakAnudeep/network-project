from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect
from users.arangodb import *
import requests

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

def add_assignment(request):
    """
    POST Request to add an assignment. (Made by te instructor.)
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
            api_url = "https://ai-context-445405667866.us-central1.run.app/build-context/"
            files = {
                'module_pdf': (assignment_file.name, assignment_file, assignment_file.content_type),
                'sample_solution_pdf': (solution_file.name, solution_file, solution_file.content_type)
            }
            data = {
                'class_code': class_code,
                'assignment_id': assignment_id
            }
            # Send the POST request to the API
            response = requests.post(api_url, files=files, data=data)

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
        return redirect('/instructor-dashboard')

    else:
        return redirect('/')

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
