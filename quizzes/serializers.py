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
