from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import Course, CourseEnrollment
from .serializers import CourseSerializer, CourseEnrollmentSerializer

from acadex.schemas import api_400, api_401


class CourseListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    @extend_schema(
        request=CourseSerializer,
        responses={
            201: CourseSerializer,
            400: api_400,
            401: api_401,
        },
        examples=[
            OpenApiExample(
                "Course Creation Example",
                value={
                    "course_code": "CSC111",
                    "title": "Introduction to Computer Science",
                    "description": "An introductory course on computer science.",
                },
                request_only=True,
            )
        ],
        tags=["Courses"],
        summary="Create a new course",
        description="This endpoint allows you to create a new course. "
                    "Only authenticated lecturer can access this endpoint.",
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={
            200: CourseSerializer(many=True),
            401: api_401,
            400: api_400,
        },
        tags=["Courses"],
        summary="List all courses",
        description="This endpoint allows you to list all courses. "
                    "Only authenticated users can access this endpoint.",
    )
    def get(self, request):
        query = request.query_params.get('search', '')
        filters = Q()

        if query:
            filters |= Q(title__icontains=query)
            filters |= Q(course_code__icontains=query)
            filters |= Q(instructor__user__first_name__icontains=query)
            filters |= Q(instructor__user__last_name__icontains=query)

        courses = Course.objects.filter(filters).distinct().order_by('course_code')
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseEnrollmentSerializer

    @extend_schema(
        responses={
            200: CourseEnrollmentSerializer,
            401: api_401,
            400: api_400,
        },
        tags=["CourseEnrollmments"],
        summary="Enroll in a course",
        description="This endpoint allows students to enroll in a course. "
                    "Only authenticated students can access this endpoint.",
    )
    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id)
        serializer = self.serializer_class(
            data=request.data, 
            context={'request': request, 'course': course})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        responses={
            200: CourseEnrollmentSerializer(many=True),
            401: api_401,
            400: api_400,
        },
        tags=["CourseEnrollmments"],
        summary="List all enrollments for a course",
        description="This endpoint allows lecturers to list all enrollments for a course. "
                    "Only authenticated lecturers can access this endpoint.",
    )
    def get(self, request, course_id):
        if not hasattr(request.user, 'lecturer_profile'):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        course = get_object_or_404(
            Course,
            course_id=course_id,
            instructor=request.user.lecturer_profile)
        enrollments = CourseEnrollment.objects.filter(course=course)
        serializer = CourseEnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class StudentEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseEnrollmentSerializer

    @extend_schema(
        responses={
            200: CourseEnrollmentSerializer(many=True),
            401: api_401,
            400: api_400,
        },
        tags=["CourseEnrollmments"],
        summary="List all courses a student is enrolled in",
        description="This endpoint allows students to list all courses they are enrolled in. "
                    "Only authenticated students can access this endpoint.",
    )
    def get(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        enrollments = CourseEnrollment.objects.filter(student=request.user.student_profile)
        serializer = self.serializer_class(enrollments, many=True)
        return Response(serializer.data)
