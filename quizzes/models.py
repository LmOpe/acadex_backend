from uuid import uuid4

from django.db import models


class Quiz(models.Model):
    """
    Model representing a quiz.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='quizzes'
    )
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    number_of_questions = models.PositiveIntegerField()
    allotted_time = models.DurationField(help_text="Format: HH:MM:SS")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.course_code}"
