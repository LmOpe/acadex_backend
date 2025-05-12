from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .serializers import (
    StudentSerializer,
    LecturerSerializer,
    LoginSerializer,
    )

from .custom_auth import acadex_auth
from .create_tokens import create_tokens_for_user

class StudentRegistrationView(APIView):
    """
    View to handle student registration.
    """

    @extend_schema(
        request=StudentSerializer,
        responses={
            status.HTTP_201_CREATED: StudentSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input"
            ),
        },
        summary="Register a new student",
        description="This endpoint allows a new student to register",
        tags=["Student Registration"],
        examples=[
            OpenApiExample(
                "Student Registration Example",
                value={
                    "matric_number": "MAT123456",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "password123",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LecturerRegistrationView(APIView):
    """
    View to handle lecturer registration.
    """

    @extend_schema(
        request=LecturerSerializer,
        responses={
            status.HTTP_201_CREATED: LecturerSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid input"
            ),
        },
        summary="Register a new lecturer",
        description="This endpoint allows a new lecturer to register",
        tags=["Lecturer Registration"],
        examples=[
            OpenApiExample(
                "Lecturer Registration Example",
                value={
                    "staff_id": "STF123456",
                    "first_name": "John",
                    "last_name": "Doe",
                    "password": "password123",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = LecturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Custom view to handle token generation for users.
    """
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Login successful",
                response={
                    "type": "object",
                    "properties": {
                        "refresh": {"type": "string"},
                        "access": {"type": "string"},
                        "user_id": {"type": "integer"},
                        "role": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"}
                    }
                }
            ),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
                description="Invalid credentials"
            )
        },
        summary="Login with credentials",
        description="Login with matric_number/password for students or \
            staff_id/password for lecturers",
        tags=["auth"]
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = acadex_auth.authenticate(request=request, username=username, password=password)
        if user:
            tokens = create_tokens_for_user(user)
            return Response({
                **tokens,
                'user_id': username,
                'user_role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
