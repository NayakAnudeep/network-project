from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    major = models.CharField(max_length=100)
    gpa = models.FloatField()
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"

class Instructor(models.Model):
    instructor_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.instructor_id})"

class Course(models.Model):
    course_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    credits = models.IntegerField()
    instructors = models.ManyToManyField(Instructor, related_name='courses')
    
    def __str__(self):
        return f"{self.name} ({self.course_id})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    term = models.IntegerField()
    year = models.IntegerField()
    final_grade = models.FloatField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'course', 'term', 'year')
    
    def __str__(self):
        return f"{self.student.name} in {self.course.name} ({self.term}/{self.year})"

class Assessment(models.Model):
    assessment_id = models.CharField(max_length=10, primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assessments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='assessments')
    term = models.IntegerField()
    year = models.IntegerField()
    type = models.CharField(max_length=50)
    date = models.DateField()
    score = models.FloatField()
    
    def __str__(self):
        return f"{self.type} for {self.student.name} in {self.course.name}"
