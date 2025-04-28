from django.contrib import admin
from .models import Student, Instructor, Course, Enrollment, Assessment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'year', 'major', 'gpa')
    search_fields = ('student_id', 'name', 'major')
    list_filter = ('year', 'major')

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('instructor_id', 'name', 'department', 'specialization')
    search_fields = ('instructor_id', 'name')
    list_filter = ('department', 'specialization')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'name', 'credits')
    search_fields = ('course_id', 'name')
    filter_horizontal = ('instructors',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'term', 'year', 'final_grade')
    search_fields = ('student__name', 'course__name')
    list_filter = ('term', 'year')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('assessment_id', 'student', 'course', 'instructor', 'type', 'date', 'score')
    search_fields = ('assessment_id', 'student__name', 'course__name', 'instructor__name')
    list_filter = ('type', 'date', 'term', 'year')
    date_hierarchy = 'date'
