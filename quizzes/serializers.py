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
