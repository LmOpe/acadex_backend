from rest_framework import serializers


from courses.models import Course

from .models import Quiz


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
