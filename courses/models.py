from uuid import uuid4
from django.db import models

class Course(models.Model):
    course_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    instructor = models.ForeignKey(
        'accounts.Lecturer',
        on_delete=models.CASCADE,
        related_name='courses'
    )
    course_code = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_code} - {self.title} - by {self.instructor.user.first_name} {self.instructor.user.last_name}"
    class Meta:
        ordering = ['course_code']
        constraints = [
            models.UniqueConstraint(fields=['course_code', 'instructor'], name='unique_course_code_per_instructor')
        ]
        
class CourseEnrollment(models.Model):
    enrollment_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} enrolled in {self.course.title}"
