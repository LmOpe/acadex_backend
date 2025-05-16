from rest_framework import serializers
from django.db import transaction


from courses.models import Course

from .models import Quiz, Question, Answer


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


class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['id']


class QuestionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerCreateSerializer(many=True, write_only=True)

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
        if not any(ans.get('is_correct') for ans in value):
            raise serializers.ValidationError(
                "At least one answer must be marked correct."
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

        if 'text' in validated_data:
            instance.text = validated_data['text']
            instance.save()

        for answer_data in answers_data:
            answer_id = answer_data.pop('id', None)
            if not answer_id:
                raise serializers.ValidationError({
                    "answers": ["Each answer must include an 'id'."]
                })

            try:
                answer_instance = instance.answers.get(id=answer_id)
                for attr, value in answer_data.items():
                    setattr(answer_instance, attr, value)
                answer_instance.save()
            except Answer.DoesNotExist as e:
                raise serializers.ValidationError({
                    "answers": [f"Answer with id '{answer_id}' does not exist for this question."]
                }) from e

        return instance
