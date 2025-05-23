from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from django.db import transaction


from courses.models import Course

from .models import (
    Quiz,
    Question,
    Answer,
    QuizAttempt,
    StudentAnswer,
)


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for the Quiz model.
    """
    class Meta:
        model = Quiz
        fields = [
            'id',
            'title',
            'instructions',
            'course',
            'start_date_time',
            'end_date_time',
            'number_of_questions',
            'allotted_time',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        start = attrs.get('start_date_time') or getattr(self.instance, 'start_date_time', None)
        end = attrs.get('end_date_time') or getattr(self.instance, 'end_date_time', None)

        if start and end and start >= end:
            raise serializers.ValidationError("Start date/time must be before end date/time.")

        now = timezone.now()

        if start and start.date() < now.date():
            raise serializers.ValidationError("Start date must be today or in the future.")

        if end and end.date() < now.date():
            raise serializers.ValidationError("End date must be today or in the future.")

        if start and start.date() == now.date() and start <= now:
            raise serializers.ValidationError("Start time must be in the future if set for today.")

        if end and end.date() == now.date() and end <= now:
            raise serializers.ValidationError("End time must be in the future if set for today.")

        return attrs


class CourseNestedSerializer(serializers.ModelSerializer):
    lecturer_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['title', 'course_code', 'lecturer_name']

    def get_lecturer_name(self, obj):
        return f"{obj.instructor.user.first_name} {obj.instructor.user.last_name}"


class QuizUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a quiz.
    """

    class Meta:
        model = Quiz
        fields = [
            'title',
            'instructions',
            'start_date_time',
            'end_date_time',
            'number_of_questions',
            'allotted_time',
            'is_active',
        ]

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())
        received_fields = set(data.keys())

        if extra_fields := received_fields - allowed_fields:
            raise serializers.ValidationError({
                "invalid_fields": f"Unexpected field(s): {', '.join(extra_fields)}"
            })

        return super().to_internal_value(data)

    def validate(self, attrs):
        start = attrs.get('start_date_time') or getattr(self.instance, 'start_date_time', None)
        end = attrs.get('end_date_time') or getattr(self.instance, 'end_date_time', None)

        if start and end and start >= end:
            raise serializers.ValidationError("Start date/time must be before end date/time.")

        now = timezone.now()

        if start and start.date() < now.date():
            raise serializers.ValidationError("Start date must be today or in the future.")

        if end and end.date() < now.date():
            raise serializers.ValidationError("End date must be today or in the future.")

        if start and start.date() == now.date() and start <= now:
            raise serializers.ValidationError("Start time must be in the future if set for today.")

        if end and end.date() == now.date() and end <= now:
            raise serializers.ValidationError("End time must be in the future if set for today.")

        return attrs


class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['id']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        include_correct = self.context.get('include_correct', True)
        if not include_correct:
            rep.pop('is_correct', None)
        return rep


class QuestionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']
        read_only_fields = ['id']

    @transaction.atomic
    def create(self, validated_data):
        quiz = self.context.get('quiz')
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(quiz=quiz, **validated_data)
        Answer.objects.bulk_create([
            Answer(question=question, **answer) for answer in answers_data
        ])
        return question

    def validate_answers(self, value):
        """
        Validates the list of answers for a question.

        Ensures that at least one answer is marked as correct.
        Raises a validation error if no correct answer is provided.
        """
        correct_count = sum(bool(answer.get('is_correct')) for answer in value)
        if correct_count != 1:
            raise serializers.ValidationError(
                "Exactly one answer must be marked as correct."
            )
        return value


class AnswerUpdateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=True)  # Only 'id' is required to locate the object

    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        extra_kwargs = {
            'text': {'required': False},
            'is_correct': {'required': False}
        }

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())
        if unexpected_fields := set(data.keys()) - allowed_fields:
            raise serializers.ValidationError({
                "non_field_errors": [f"Unexpected fields: {', '.join(unexpected_fields)}"]
            })
        return super().to_internal_value(data)


class QuestionUpdateSerializer(serializers.ModelSerializer):
    answers = AnswerUpdateSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']
        extra_kwargs = {
            'text': {'required': False}
        }

    @transaction.atomic
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])

        instance.text = validated_data.get('text', instance.text)
        instance.save()

        existing_answer_ids = {str(ans.id) for ans in instance.answers.all()}

        for ans_data in answers_data:
            ans_id = str(ans_data.get("id"))
            if not ans_id or ans_id not in existing_answer_ids:
                raise serializers.ValidationError({
                    "answers": f"Answer with id '{ans_id}' does not belong to this question."
                })

        answer_update_map = {str(a['id']): a for a in answers_data}
        final_states = []

        for answer in instance.answers.all():
            if updated := answer_update_map.get(str(answer.id)):
                is_correct = updated.get('is_correct', answer.is_correct)
                if is_correct is not None:
                    is_correct = bool(is_correct)
                text = updated.get('text', answer.text)
            else:
                is_correct = answer.is_correct
                text = answer.text

            final_states.append({
                'id': answer.id,
                'text': text,
                'is_correct': is_correct
            })
        if sum(bool(ans['is_correct']) for ans in final_states) != 1:
            raise serializers.ValidationError({
                "answers": "Exactly one answer must be marked as correct after update."
            })

        for answer in instance.answers.all():
            if data := answer_update_map.get(str(answer.id)):
                if 'text' in data:
                    answer.text = data['text']
                if 'is_correct' in data:
                    answer.is_correct = bool(data['is_correct'])
                answer.save()
        return instance


class QuizAttemptCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['attempt_id', 'attempt_time', 'end_time']
        read_only_fields = ['attempt_id', 'attempt_time', 'end_time']

    def validate(self, attrs):
        quiz = self.context.get('quiz')
        student = self.context.get('student')

        if not quiz or not student:
            raise serializers.ValidationError("Quiz and student must be provided.")

        if QuizAttempt.objects.filter(quiz=quiz, student=student).exists():
            raise serializers.ValidationError("You have already attempted this quiz.")

        now = timezone.now()
        if quiz.start_date_time > now:
            raise serializers.ValidationError("Quiz has not started yet.")
        if quiz.end_date_time < now:
            raise serializers.ValidationError("Quiz has already ended.")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        quiz = self.context.get("quiz")
        student = self.context.get("student")
        now = timezone.now()

        allotted = quiz.allotted_time or timedelta()
        scheduled_end = quiz.end_date_time
        calculated_end = now + allotted
        final_end = min(calculated_end, scheduled_end)

        return QuizAttempt.objects.create(
            quiz=quiz,
            student=student,
            attempt_time=now,
            end_time=final_end
        )


class QuizAttemptResponseSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    end_time = serializers.DateTimeField()
    quiz_questions = QuestionCreateSerializer(many=True)


class StudentAnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_option_id = serializers.UUIDField()


class StudentQuizSubmissionSerializer(serializers.Serializer):
    attempt_id = serializers.UUIDField()
    answers = StudentAnswerSubmissionSerializer(many=True)

    def validate(self, data):
        attempt = QuizAttempt.objects.select_related(
            'quiz', 'student').get(attempt_id=data.get('attempt_id'))
        now = timezone.now()
        grace_period = timedelta(minutes=1)

        if now > (attempt.end_time + grace_period):
            raise serializers.ValidationError("Submission time has passed.")

        if attempt.student_answers.exists():
            raise serializers.ValidationError(
                "You have already submitted this quiz."
            )

        self.context['attempt'] = attempt
        return data

    @transaction.atomic
    def create(self, validated_data):
        attempt = self.context.get('attempt')
        answers_data = validated_data.get('answers')

        correct_count = 0
        response_data = []
        answered_question_ids = set()

        for answer_data in answers_data:
            question_id = answer_data.get('question_id')
            selected_option_id = answer_data.get('selected_option_id')

            try:
                question = Question.objects.get(
                    id=question_id,
                    quiz=attempt.quiz
                )
            except Question.DoesNotExist as e:
                raise serializers.ValidationError({
                    "question_id":
                        f"Invalid question ID {question_id} for this quiz."
                }) from e

            try:
                selected_option = Answer.objects.get(
                    id=selected_option_id,
                    question=question
                )
            except Answer.DoesNotExist as e:
                raise serializers.ValidationError({
                    "selected_option_id": (
                        f"Invalid answer ID {selected_option_id}"
                        f" for question {question_id}"
                    )}) from e

            is_correct = selected_option.is_correct
            if is_correct:
                correct_count += 1

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct,
            )

            answered_question_ids.add(question.id)

            response_item = {
                "question_id": str(question.id),
                "question_text": question.text,
                "selected_option_text": selected_option.text,
                "is_correct": is_correct
            }

            if not is_correct:
                if correct_option := question.answers.filter(
                    is_correct=True
                ).first():
                    response_item["correct_option_text"] = correct_option.text

            response_data.append(response_item)

        # Handle unanswered questions
        all_questions = Question.objects.filter(
            quiz=attempt.quiz
        ).prefetch_related('answers')
        for question in all_questions:
            if question.id not in answered_question_ids:
                correct_option = question.answers.filter(
                    is_correct=True
                ).first()
                response_data.append({
                    "question_id": str(question.id),
                    "question_text": question.text,
                    "selected_option_text": None,
                    "is_correct": False,
                    "correct_option_text": (
                        correct_option.text if correct_option else None
                    )
                })

        attempt.score = correct_count
        attempt.save()

        return {
            "score": correct_count,
            "quiz_questions": response_data
        }


class StudentAnswerFeedbackSerializer(serializers.Serializer):
    question_id = serializers.UUIDField()
    selected_option = serializers.CharField()
    is_correct = serializers.BooleanField()
    correct_option = serializers.CharField(required=False)


class StudentQuizAnswerResponseSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    answers = StudentAnswerFeedbackSerializer(many=True)
