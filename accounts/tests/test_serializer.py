# tests/test_serializers.py
import pytest
from accounts.serializers import StudentSerializer, LecturerSerializer
from accounts.models import Student, Lecturer

@pytest.mark.django_db
def test_student_serializer_creates_user_and_student():
    data = {
        "matric_number": "MAT999999",
        "first_name": "New",
        "last_name": "Student",
        "email": "new@student.com",
        "password": "newpass123"
    }
    serializer = StudentSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    student = serializer.save()
    assert isinstance(student, Student)
    assert student.matric_number == "MAT999999"
    assert student.user.first_name == "New"
    assert student.user.check_password("newpass123")
    assert student.user.role == "STUDENT"

@pytest.mark.django_db
def test_lecturer_serializer_creates_user_and_lecturer():
    data = {
        "staff_id": "STF999999",
        "first_name": "New",
        "last_name": "Lecturer",
        "email": "new@lecturer.com",
        "password": "newpass123"
    }
    serializer = LecturerSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    lecturer = serializer.save()
    assert isinstance(lecturer, Lecturer)
    assert lecturer.staff_id == "STF999999"
    assert lecturer.user.first_name == "New"
    assert lecturer.user.check_password("newpass123")
    assert lecturer.user.role == "LECTURER"

@pytest.mark.django_db
def test_student_serializer_validation_error_missing_required_fields():
    data = {"matric_number": "MAT123456"}
    serializer = StudentSerializer(data=data)
    assert not serializer.is_valid()
    assert "first_name" in serializer.errors
    assert "last_name" in serializer.errors
    assert "password" in serializer.errors

@pytest.mark.django_db
def test_lecturer_serializer_validation_error_missing_required_fields():
    data = {"staff_id": "STF123456"}
    serializer = LecturerSerializer(data=data)
    assert not serializer.is_valid()
    assert "first_name" in serializer.errors
    assert "last_name" in serializer.errors
    assert "password" in serializer.errors
