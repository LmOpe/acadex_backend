from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course, CourseEnrollment
from accounts.models import Student, Lecturer

from .models import Quiz
from .serializers import QuizSerializer

from acadex.permissions import IsCourseInstructor
from acadex.schemas import api_400, api_401, api_403

class QuizCreateView(APIView):
    """
    API view to create a new quiz.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=QuizSerializer,
        responses={
            201: OpenApiResponse(
                response=QuizSerializer,
                description="Quiz created successfully.",
                examples=[
                    OpenApiExample(
                        name="Quiz Created",
                        value={
                            "title": "Midterm Quiz",
                            "instructions": "Answer all questions. No external help.",
                            "course": "af32b-4c3d-8f9e-1a2b3c4d5e6f",
                            "start_date_time": "2025-06-01T09:00:00Z",
                            "end_date_time": "2025-06-01T10:00:00Z",
                            "number_of_questions": 10,
                            "allotted_time": "00:30:00",
                            "is_active": True,
                        }
                    )
                ]
            ),
            200: OpenApiResponse(
                response=QuizSerializer,
                description="Quiz retrieved successfully.",
                examples=[
                    OpenApiExample(
                        name="Quiz Details",
                        value={
                            "id": "d9d8-asd9-asd8-asd8",
                            "title": "Midterm Quiz",
                            "instructions": "Answer all questions. No external help.",
                            "course": "af32b-4c3d-8f9e-1a2b3c4d5e6f",
                            "start_date_time": "2025-06-01T09:00:00Z",
                            "end_date_time": "2025-06-01T10:00:00Z",
                            "number_of_questions": 10,
                            "allotted_time": "00:30:00",
                            "is_active": True,
                            "created_at": "2025-05-14T10:00:00Z"
                        }
                    )
                ]
            ),
            403: api_403,
            401: api_401,
            400: api_400,
        },
        summary="Create a new quiz",
        description="This endpoint allows instructors to create a new quiz for a specific course. The instructor must be enrolled in the course to create a quiz.",
        tags=["Quizzes"],
    )
    def post(self, request, *args, **kwargs):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not hasattr(user, 'lecturer_profile'):
                return Response(
                    {"detail": "You do not have permission to create a quiz."},
                    status=status.HTTP_403_FORBIDDEN
                )
            course = serializer.validated_data.get('course')
            if course.instructor != user.lecturer_profile:
                return Response(
                    {"detail": "You do not have permission to create a quiz for this course."},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class QuizListView(APIView):
    """
    API view to list quizzes for a course. 
    Students see active quizzes, and lecturers can see quizzes with a filter for `is_active`.
    """
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    def get(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'student_profile'):
            student = user.student_profile
            enrolled_courses = CourseEnrollment.objects.filter(student=student).values_list('course', flat=True)
            quizzes = Quiz.objects.filter(course__in=enrolled_courses, is_active=True)
        elif hasattr(user, 'lecturer_profile'):
            lecturer = user.lecturer_profile
            courses = Course.objects.filter(instructor=lecturer)
            is_active = request.query_params.get('is_active', None)
            if is_active is not None:
                quizzes = Quiz.objects.filter(course__in=courses, is_active=is_active)
            else:
                quizzes = Quiz.objects.filter(course__in=courses)
        else:
            quizzes = Quiz.objects.none()

        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
