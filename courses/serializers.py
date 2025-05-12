from rest_framework import serializers

from .models import Course, CourseEnrollment

class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'course_id',
            'course_code',
            'title',
            'description',
            'created_at',
            'instructor_name'
        ]
        read_only_fields = ['course_id', 'instructor_name','created_at']
        
    def get_instructor_name(self, obj):
        return f"{obj.instructor.user.first_name} {obj.instructor.user.last_name}"
    
    def validate(self, attrs):
        request = self.context.get('request')
        instructor = request.user.lecturer_profile if hasattr(request.user, 'lecturer_profile') else None
        course_code = attrs.get('course_code')
        
        if instructor and Course.objects.filter(course_code=course_code, instructor=instructor).exists():
            raise serializers.ValidationError(
                {"course_code": "You already have a course with this code."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'lecturer_profile'):
            validated_data['instructor'] = request.user.lecturer_profile
        else:
            raise serializers.ValidationError("Authenticated user is not a lecturer.")  
        return super().create(validated_data)
    
class CourseEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    course_title = serializers.SerializerMethodField(source='course.title', read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = [
            'enrollment_id',
            'student',
            'course',
            'enrollment_date',
            'student_name',
            'course_title',
        ]
        read_only_fields = ['enrollment_id', 'student_name', 'course_title', 'enrollment_date']
        
        def get_student_name(self, obj):
            return f"{obj.student.user.first_name} {obj.student.user.last_name}"
        
        def create(self, validated_data):
            request = self.context.get('request')
            if request and hasattr(request.user, 'student'):
                validated_data['student'] = request.user.student
            return super().create(validated_data)
