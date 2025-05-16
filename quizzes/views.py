from collections import defaultdict

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from courses.models import Course, CourseEnrollment

from .models import Quiz, Question
from .serializers import (
    QuizSerializer,
    CourseNestedSerializer,
    QuizUpdateSerializer,
    QuestionCreateSerializer,
    QuestionUpdateSerializer,
)

from acadex.permissions import IsCourseInstructor, IsLecturer
from acadex.schemas import api_400, api_401, api_403
from acadex.utils import str_to_bool


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
                        },
                    )
                ],
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
            if not hasattr(user, "lecturer_profile"):
                return Response(
                    {"detail": "You do not have permission to create a quiz."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            course = serializer.validated_data.get("course")
            if course.instructor != user.lecturer_profile:
                return Response(
                    {
                        "detail": "You do not have permission to create a quiz for this course."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizListView(APIView):
    """
    API view to list quizzes for a course.
    Students see active quizzes, and lecturers can see quizzes with a filter for `is_active`.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=QuizSerializer(many=True),
                description="List of quizzes for the course.",
                examples=[
                    OpenApiExample(
                        name="Quizzes List",
                        value=[
                            {
                                "course_id": "4e798140-66aa-40cb-84d4-6653ce0a7392",
                                "course_details": {
                                    "course_id": "4e798140-66aa-40cb-84d4-6653ce0a7392",
                                    "title": "Introduction to Computer Science",
                                    "course_code": "CSC111",
                                    "lecturer_name": "John Doe",
                                },
                                "quizzes": [
                                    {
                                        "id": "be7b6439-a3fb-4428-a653-279763c900b7",
                                        "title": "Midterm Quiz",
                                        "instructions": "Answer all questions. No external help.",
                                        "course": "4e798140-66aa-40cb-84d4-6653ce0a7392",
                                        "start_date_time": "2025-05-14T01:52:37.900000Z",
                                        "end_date_time": "2025-05-14T01:52:37.900000Z",
                                        "number_of_questions": 10,
                                        "allotted_time": "00:30:00",
                                        "is_active": True,
                                        "created_at": "2025-05-14T02:01:56.850857Z",
                                    }
                                ],
                            }
                        ],
                    )
                ],
            ),
            403: api_403,
            401: api_401,
            400: api_400,
        },
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=bool,
                required=False,
                description="Lecturers filter quizzes by active status. True for active quizzes, False for inactive quizzes.",
            )
        ],
        summary="List quizzes for a course",
        description="This endpoint allows students to list active quizzes and lecturers to filter quizzes by `is_active` status.",
        tags=["Quizzes"],
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, "student_profile"):
            student = user.student_profile
            enrolled_courses = CourseEnrollment.objects.filter(
                student=student
            ).values_list("course", flat=True)
            quizzes = Quiz.objects.filter(
                course__in=enrolled_courses, is_active=True)
        elif hasattr(user, "lecturer_profile"):
            lecturer = user.lecturer_profile
            courses = Course.objects.filter(instructor=lecturer)
            is_active = request.query_params.get("is_active", None)
            if is_active is not None:
                is_active = str_to_bool(is_active)
                quizzes = Quiz.objects.filter(
                    course__in=courses, is_active=is_active)
            else:
                quizzes = Quiz.objects.filter(course__in=courses)
        else:
            return Response([])

        grouped_data = defaultdict(
            lambda: {"course_details": None, "quizzes": []})

        for quiz in quizzes:
            course = quiz.course
            course_id = str(course.course_id)

            if grouped_data[course_id]["course_details"] is None:
                grouped_data[course_id]["course_details"] = CourseNestedSerializer(
                    course
                ).data

            grouped_data[course_id]["quizzes"].append(
                QuizSerializer(quiz).data)

        result = [
            {
                "course_id": course_id,
                "course_details": data["course_details"],
                "quizzes": data["quizzes"],
            }
            for course_id, data in grouped_data.items()
        ]

        return Response(result)


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    serializer_class = QuizUpdateSerializer

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=QuizSerializer,
                description="Quiz details updated successfully.",
                examples=[
                    OpenApiExample(
                        name="Quiz Details",
                        value={
                            "title": "Midterm Quiz",
                            "instructions": "Answer all questions. No external help.",
                            "start_date_time": "2025-06-01T09:00:00Z",
                            "end_date_time": "2025-06-01T10:00:00Z",
                            "number_of_questions": 10,
                            "allotted_time": "00:30:00",
                            "is_active": True,
                        },
                    )
                ],
            ),
            403: api_403,
            401: api_401,
            400: api_400,
        },
        summary="Update quiz details",
        description="This endpoint allows instructors to update details of a specific quiz.",
        tags=["Quizzes"],
    )
    def put(self, request, quiz_id, *args, **kwargs):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Quiz not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.check_object_permissions(request, quiz)

        data = request.data
        serializer = self.serializer_class(quiz, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "data": serializer.validated_data,
                    "detail": "Quiz updated successfully."
                    },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    serializer_class = QuestionCreateSerializer

    @extend_schema(
        request=QuestionCreateSerializer(many=True),
        responses={201: QuestionCreateSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Bulk Question and Answer Creation",
                value=[
                    {
                        "text": "What is the capital of France?",
                        "answers": [
                            {"text": "Paris", "is_correct": True},
                            {"text": "Lyon", "is_correct": False},
                            {"text": "Marseille", "is_correct": False}
                        ]
                    },
                    {
                        "text": "Which planet is known as the Red Planet?",
                        "answers": [
                            {"text": "Earth", "is_correct": False},
                            {"text": "Mars", "is_correct": True},
                            {"text": "Jupiter", "is_correct": False}
                        ]
                    }
                ],
                request_only=True
            )
        ],
        description=(
            "Create multiple questions and answers for a given quiz."
            "Each question must have at least one correct answer."
        ),
        parameters=[
            OpenApiParameter(
                name="quiz_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the quiz"
            )
        ]
    )
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Quiz not found."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.check_object_permissions(request, quiz)

        if Question.objects.filter(quiz=quiz).exists():
            return Response(
                {"detail": "Questions have already been set for this quiz."},
                status=status.HTTP_400_BAD_REQUEST,
                )

        expected_count = quiz.number_of_questions
        actual_count = len(request.data)
        if actual_count != expected_count:
            return Response(
                {
                    "detail":
                        (
                            f"Expected {expected_count} questions, "
                            f"but got {actual_count}."
                        )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(
            data=request.data,
            many=True,
            context={'quiz': quiz}
        )
        if serializer.is_valid():
            questions = serializer.save()
            return Response(
                {"data": QuestionCreateSerializer(questions, many=True).data},
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class QuestionUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsCourseInstructor]
    serializer_class = QuestionUpdateSerializer

    @extend_schema(
        request=QuestionUpdateSerializer,
        responses={200: QuestionUpdateSerializer},
        examples=[
            OpenApiExample(
                name="Update question and answers",
                request_only=True,
                value={
                    "text": "What is the capital of France?",
                    "answers": [
                        {"id": "a1", "text": "Paris", "is_correct": True},
                        {"id": "a2", "text": "London", "is_correct": False},
                        {"id": "a3", "text": "Berlin", "is_correct": False},
                        {"id": "a4", "text": "Madrid", "is_correct": False},
                    ]
                }
            ),
            OpenApiExample(
                name="Successful update response",
                response_only=True,
                value={
                    "id": "q1",
                    "text": "What is the capital of France?",
                    "answers": [
                        {"id": "a1", "text": "Paris", "is_correct": True},
                        {"id": "a2", "text": "London", "is_correct": False},
                        {"id": "a3", "text": "Berlin", "is_correct": False},
                        {"id": "a4", "text": "Madrid", "is_correct": False},
                    ]
                }
            )
        ],
        description=(
            "Update question and answers for a given quiz."
        ),
        parameters=[
            OpenApiParameter(
                name="quiz_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the quiz"
            ),
            OpenApiParameter(
                name="question_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID of the question"
            )
        ]
    )
    def put(self, request, quiz_id, question_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {"detail": "Quiz not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, quiz)

        try:
            question = quiz.questions.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"detail": "Question not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(question, data=request.data)
        if serializer.is_valid():
            updated_question = serializer.save()
            return Response(
                self.serializer_class(updated_question).data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
