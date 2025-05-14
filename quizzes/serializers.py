from rest_framework import serializers
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
