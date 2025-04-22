
from arango import ArangoClient
from django.conf import settings
import bcrypt
from datetime import datetime

# Construct the full ArangoDB connection URL
arangodb_url = f"{settings.ARANGO_DB['HOST']}:{settings.ARANGO_DB['PORT']}"

# Initialize the ArangoDB client with the full URL
client = ArangoClient(hosts=arangodb_url)

# Ensure the database exists before using it
sys_db = client.db("_system", username=settings.ARANGO_DB['USERNAME'], password=settings.ARANGO_DB['PASSWORD'])
if not sys_db.has_database(settings.ARANGO_DB['DATABASE']):
    sys_db.create_database(settings.ARANGO_DB['DATABASE'])

# Now connect to the correct database
db = client.db(settings.ARANGO_DB['DATABASE'],
               username=settings.ARANGO_DB['USERNAME'],
               password=settings.ARANGO_DB['PASSWORD'])

# ┌─────────────────┐
# │ Database Tables │
# └─────────────────┘
# Check if the 'users' collection exists, create if missing
if not db.has_collection('users'):
    db.create_collection('users')

if not db.has_collection('submission'):
    db.create_collection('submission')

if not db.has_collection('courses'):
    db.create_collection('courses')
# ┌───────────────────┐
# │ Updates & Queries │
# └───────────────────┘
# Function to create a new user
def register_user(username, email, password, role="student"):
    users = db.collection('users')

    # Check if the email already exists
    existing_user = list(users.find({"email": email}))
    if existing_user:
        return {"error": "User already exists"}

    # Hash the password
    hashed_pswd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user data
    user_data = {
        "username": username,
        "email": email,
        "password_hash": hashed_pswd.decode('utf-8'),
        "role": role,
        "created_at": datetime.utcnow().isoformat(),
        "courses": []
    }

    users.insert(user_data)
    return {"success": "User registration successful"}

def authenticate_user(email, password):
    users = db.collection('users')
    user_list = list(users.find({'email': email}))

    if user_list:
        user = user_list[0]
        if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode("utf-8")):
            return {
                "failure": None,
                "user_id": user["_id"],
                "username": user["username"],
                "role": user["role"]
            }
        else:
            return {"failure": "Invalid credentials" }

    return {"failure": "Invalid credentials"}

def db_add_course(class_code, class_title, instructor_id):
    """
    Add a course to the database.
    Returns None if successful, otherwise, an error message string.
    """
    print(instructor_id, flush=True)
    courses = db.collection('courses')
    existing_course = list(courses.find({"class_code": class_code}))
    if existing_course:
        return "Course already exists."
    courses.insert({
        "class_code": class_code,
        "class_title": class_title,
        "instructor_id": instructor_id,
        "assignments": []
    })

def db_get_course_assignments(class_code):
    """
    Returns info for course, and an indicator of whether there was an error.
    """
    # Get the course with its assignments
    courses = db.collection('courses')
    course_list = list(courses.find({"class_code": class_code}))
    if not course_list:
        return []

    course = course_list[0]
    assignments = course.get('assignments', [])
    # print(assignments, flush=True)

    return { "code": class_code, "assignments": assignments }, None

def db_instructor_courses(instructor_id):
    courses = db.collection('courses')
    courses_list = list(courses.find({"instructor_id": instructor_id}))
    return courses_list

def db_enroll_student_in_course(user_id, class_code):
    users = db.collection('users')

    try:
        user = users.get(user_id)
        if not user:
            return "User not found."

        courses = db.collection('courses')
        course = list(courses.find({"class_code": class_code}))
        if not course:
            return "Course not found."

        if "courses" not in user:
            user["courses"] = []

        if class_code in user["courses"]:
            return "Student has already added this course."

        user["courses"].append(class_code)
        users.update(user)

        return None # success
    except Exception as e:
        return f"Error: {str(e)}"

def student_courses_overview(user_id) -> dict:
    print("HYAR", flush=True)
    users = db.collection('users')
    user_list = list(users.find({"_id": user_id}))
    print("user_list", user_list, flush=True)
    if not user_list:
        return {"courses": []}

    user_info = user_list[0]
    course_codes = user_info.get("courses", [])
    print("course_codes", course_codes, flush=True)
    courses = db.collection('courses')
    courses_data = []
    # user_list [{'_key': '20773', '_id': 'users/20773', '_rev': '_jcfHWsq---', 'username': 'Bobo Fish', 'email': 'bobofish@fish.com', 'password_hash': '$2b$12$dsrSPntSWEQCYkQQeR6uWep0pIxZwkpgou4clr0b1v726N7SKhLTu', 'role': 'student', 'created_at': '2025-03-30T18:21:18.442794'}]
    for code in course_codes:
        course_list = list(courses.find({"class_code": code}))
        print("course_list:", course_list, flush=True)
        if course_list:
            course = course_list[0]

            # Find pending assignments
            pending_assignments = get_pending_assignments(code, user_id)

            courses_data.append({
                "code": course["class_code"],
                "title": course["class_title"],
                "instructor": get_instructor_name(course["instructor_id"]),
                "schedule": course.get("schedule", "Not specified"),
                "n_pending_assignments": len(pending_assignments),
                "next_due_date": get_next_due_date(pending_assignments),
                "id": course["_id"]
            })
        else:
            print("no course_list", flush=True)

    return {"courses": courses_data}


def get_pending_assignments(class_code, user_id):
    """
    Get assignments that haven't been submitted by the user yet

    Parameters:
    - class_code: The course code
    - user_id: The student's user ID

    Returns:
    - List of pending assignment objects
    """
    # Get the course with its assignments
    courses = db.collection('courses')
    course_list = list(courses.find({"class_code": class_code}))

    if not course_list:
        return []

    course = course_list[0]
    assignments = course.get('assignments', [])

    # Get the student's submissions for this course
    submissions = db.collection('submission')
    student_submissions = list(submissions.find({
        "user_id": user_id,
        "class_code": class_code
    }))

    # Create a set of submitted assignment IDs for quick lookup
    submitted_assignment_ids = {sub.get("assignment_id") for sub in student_submissions}

    # Filter assignments to only include those that haven't been submitted
    pending = [a for a in assignments if a.get("id") not in submitted_assignment_ids]

    return pending

def get_next_due_date(pending_assignments):
    if not pending_assignments:
        return None

    # Sort assignments by due date and return the nearest one
    sorted_assignments = sorted(pending_assignments, key=lambda x: x.get("due_date", ""))
    if sorted_assignments:
        due_date = sorted_assignments[0].get("due_date")
        if due_date:
            return due_date
    return None

def get_instructor_name(instructor_id):
    instructor = list(db.collection('users').find({"_id": instructor_id}))
    if instructor:
        return instructor[0].get("username", "Unknown")
    return "Unknown"

def db_get_class_assignment_submissions(class_code, assignment_id): # TODO
    return []

def db_create_assignment(class_code, assignment_name, description, due_date=None, total_points=100):
    """
    Add a new assignment to a course.

    Parameters:
    - class_code: The code identifying the course
    - assignment_name: Name of the assignment
    - description: Detailed description of the assignment
    - due_date: Due date for the assignment (ISO format string)
    - total_points: Maximum points for the assignment

    Returns:
    - None if successful, otherwise an error message string
    """
    try:
        courses = db.collection('courses')
        course_list = list(courses.find({"class_code": class_code}))

        if not course_list:
            return "Course not found."

        course = course_list[0]

        # Create a unique assignment ID within the course
        assignment_id = f"{class_code}_{len(course.get('assignments', []))}"

        # Create the assignment object
        new_assignment = {
            "id": assignment_id,
            "name": assignment_name,
            "description": description,
            "due_date": due_date,
            "total_points": total_points,
            "created_at": datetime.utcnow().isoformat()
        }

        # Add the assignment to the course's assignments array
        if "assignments" not in course:
            course["assignments"] = []

        course["assignments"].append(new_assignment)

        # Update the course in the database
        courses.update(course)

        return None  # Success
    except Exception as e:
        return f"Error creating assignment: {str(e)}"

def db_get_assignment_id(class_code, assignment_name):
    try:
        courses = db.collection('courses')
        course_list = list(courses.find({"class_code": class_code}))

        if not course_list:
            return None  # Course not found

        course = course_list[0]

        # Check if assignments exist in the course
        if "assignments" not in course or not course["assignments"]:
            return None  # No assignments in this course

        # Find the assignment by name
        for assignment in course["assignments"]:
            if assignment.get("name") == assignment_name:
                return assignment.get("id")  # Return the assignment's key/ID

        return None  # Assignment not found

    except Exception as e:
        print(f"Error retrieving assignment ID: {str(e)}")
        return None


def db_get_student_assignments(user_id, class_code=None):
    """
    Retrieve assignments for a student, optionally filtered by class code.

    Parameters:
    - user_id: The ID of the student
    - class_code: Optional class code to filter assignments

    Returns:
    - Dictionary containing assignments grouped by course, with submission status
    """
    try:
        # Verify user exists and is a student
        users = db.collection('users')
        user = users.get(user_id)

        if not user or user.get('role') != 'student':
            return {"error": "Invalid student ID"}

        # Get courses the student is enrolled in
        enrolled_courses = user.get('courses', [])
        if not enrolled_courses:
            return {"assignments": []}

        # Filter by specific class if provided
        if class_code:
            if class_code not in enrolled_courses:
                return {"error": "Student not enrolled in this course"}
            enrolled_courses = [class_code]

        # Get course data including assignments
        courses = db.collection('courses')
        submissions = db.collection('submission')

        result = []

        for code in enrolled_courses:
            course_list = list(courses.find({"class_code": code}))
            if not course_list:
                continue

            course = course_list[0]
            assignments = course.get('assignments', [])

            # Get student's submissions for this course
            student_submissions = list(submissions.find({
                "user_id": user_id,
                "class_code": code
            }))

            # Create a map of assignment ID to submission for quick lookup
            submission_map = {sub.get('assignment_id'): sub for sub in student_submissions}

            course_assignments = []
            for assignment in assignments:
                assignment_id = assignment.get('id')
                submission = submission_map.get(assignment_id)

                # Determine status and grade
                status = "Not Submitted"
                grade = None
                feedback = None

                if submission:
                    status = "Submitted"
                    grade = submission.get('grade')
                    feedback = submission.get('feedback')
                    if grade is not None:
                        status = "Graded"

                course_assignments.append({
                    "id": assignment_id,
                    "name": assignment.get('name'),
                    "description": assignment.get('description'),
                    "due_date": assignment.get('due_date'),
                    "total_points": assignment.get('total_points', 100),
                    "status": status,
                    "grade": grade,
                    "feedback": feedback
                })

            # Add course with its assignments to the result
            if course_assignments:
                result.append({
                    "class_code": code,
                    "class_title": course.get('class_title'),
                    "assignments": course_assignments
                })

        return {"assignments": result}

    except Exception as e:
        return {"error": f"Error retrieving assignments: {str(e)}"}

def db_add_submission(user_id, class_code, assignment_id, file_content, file_name):
    """
    Add a new submission for an assignment.

    Parameters:
    - user_id: The ID of the student submitting the assignment
    - class_code: The code of the class the assignment belongs to
    - assignment_id: The ID of the assignment
    - file_content: The binary content of the PDF file
    - file_name: The name of the uploaded file

    Returns:
    - None if successful, otherwise an error message string
    """
    try:
        # Verify the assignment exists
        courses = db.collection('courses')
        course_list = list(courses.find({"class_code": class_code}))

        if not course_list:
            return "Course not found."

        course = course_list[0]
        assignment_exists = False

        for assignment in course.get('assignments', []):
            if assignment.get('id') == assignment_id:
                assignment_exists = True
                break

        if not assignment_exists:
            return "Assignment not found."

        # Check if the student is enrolled in this course
        users = db.collection('users')
        user = users.get(user_id)

        if not user or class_code not in user.get('courses', []):
            return "Student is not enrolled in this course."

        # Check if there's an existing submission
        submissions = db.collection('submission')
        existing_submission = list(submissions.find({
            "user_id": user_id,
            "class_code": class_code,
            "assignment_id": assignment_id
        }))

        submission_data = {
            "user_id": user_id,
            "class_code": class_code,
            "assignment_id": assignment_id,
            "file_name": file_name,
            "file_content": file_content,  # Store binary content
            "submission_date": datetime.now().isoformat(),
            "grade": None,
            "feedback": None,
            "graded": False
        }

        if existing_submission:
            # Update existing submission
            submission_doc = existing_submission[0]
            submission_doc.update(submission_data)
            submissions.update(submission_doc)
            return None  # Success
        else:
            # Create new submission
            submissions.insert(submission_data)
            return None  # Success

    except Exception as e:
        return f"Error processing submission: {str(e)}"

def db_get_submission(user_id, class_code, assignment_id):
    """
    Retrieve a specific submission for a student.

    Parameters:
    - user_id: The ID of the student
    - class_code: The code of the class
    - assignment_id: The ID of the assignment

    Returns:
    - The submission document if found, otherwise None
    """
    try:
        submissions = db.collection('submission')
        submission_list = list(submissions.find({
            "user_id": user_id,
            "class_code": class_code,
            "assignment_id": assignment_id
        }))

        if submission_list:
            return submission_list[0]
        else:
            return None

    except Exception as e:
        print(f"Error retrieving submission: {str(e)}")
        return None

def db_get_submission_by_id(submission_numeric_id):
    """Retrieve submission by numeric portion of ID"""
    try:
        full_id = f"submission/{submission_numeric_id}"
        submissions = db.collection('submission')
        return submissions.get(full_id)
    except Exception as e:
        print(f"Error retrieving submission: {str(e)}")
        return None
