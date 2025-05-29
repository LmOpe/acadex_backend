# tests/test_auth_backend.py
import pytest
from accounts.custom_auth import AcadexAuthBackend

@pytest.mark.django_db
def test_authenticate_with_student_correct_password(student_user):
    backend = AcadexAuthBackend()
    user = backend.authenticate(None, username=student_user.matric_number, password="testpass123")
    assert user == student_user.user

@pytest.mark.django_db
def test_authenticate_with_lecturer_correct_password(lecturer_user):
    backend = AcadexAuthBackend()
    user = backend.authenticate(None, username=lecturer_user.staff_id, password="testpass123")
    assert user == lecturer_user.user

@pytest.mark.django_db
@pytest.mark.parametrize("username,password", [
    ("wrongmatric", "studentpass"),
    ("MAT123456", "wrongpass"),
    ("wrongstaff", "lecturerpass"),
    ("STF654321", "wrongpass"),
])
def test_authenticate_with_invalid_credentials(student_user, lecturer_user, username, password):
    backend = AcadexAuthBackend()
    user = backend.authenticate(None, username=username, password=password)
    assert user is None

@pytest.mark.django_db
def test_authenticate_with_empty_username_or_password(student_user):
    backend = AcadexAuthBackend()
    assert backend.authenticate(None, username=None, password="pass") is None
    assert backend.authenticate(None, username="MAT123456", password=None) is None
    assert backend.authenticate(None, username=None, password=None) is None

@pytest.mark.django_db
def test_authenticate_with_inactive_user(inactive_user):
    backend = AcadexAuthBackend()
    user = backend.authenticate(None, username=inactive_user.matric_number, password="inactivepass")
    assert user is None
