import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import Student, Lecturer

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_user(db):
    user = User.objects.create_user(
        first_name="Student",
        last_name="Test",
        email="student@example.com",
        password="testpass123",
        role="STUDENT"
    )
    student = Student.objects.create(user=user, matric_number="MAT123456")
    return student


@pytest.fixture
def lecturer_user(db):
    user = User.objects.create_user(
        first_name="Lecturer",
        last_name="Test",
        email="lecturer@example.com",
        password="testpass123",
        role="LECTURER"
    )
    lecturer = Lecturer.objects.create(user=user, staff_id="STF123456")
    return lecturer

@pytest.fixture
def inactive_user(db):
    user = User.objects.create_user(
        first_name="Lecturer",
        last_name="Test",
        email="lecturer@example.com",
        password="testpass123",
        role="LECTURER",
        is_active=False
    )
    student = Student.objects.create(user=user, matric_number="MAT123456")
    return student
