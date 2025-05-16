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


class Question(models.Model):
    """
    Model representing a question in a quiz.
    
    Each question is associated with a specific quiz and contains the question text.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
    Model representing an answer to a quiz question.

    Each answer is linked to a specific question and indicates whether it is correct.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"
