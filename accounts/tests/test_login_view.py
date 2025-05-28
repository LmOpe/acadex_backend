# tests/test_login_view.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_student_success(api_client, student_user):
    url = reverse('token_obtain_pair')
    data = {
        "username": student_user.matric_number,
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data['user_id'] == student_user.matric_number
    assert response.data['user_role'] == "STUDENT"

@pytest.mark.django_db
def test_login_lecturer_success(api_client, lecturer_user):
    url = reverse('token_obtain_pair')
    data = {
        "username": lecturer_user.staff_id,
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data['user_id'] == lecturer_user.staff_id
    assert response.data['user_role'] == "LECTURER"

@pytest.mark.django_db
@pytest.mark.parametrize("username,password", [
    ("nonexistent", "somepass"),
    ("MAT123456", "wrongpass"),
    ("STF654321", "wrongpass"),
    ("", ""),
    (None, None),
])
def test_login_failure_invalid_credentials(api_client, username, password):
    url = reverse('token_obtain_pair')
    data = {
        "username": username,
        "password": password
    }
    response = api_client.post(url, data, format='json')
    # For None username or password, serializer.is_valid() will fail, so expect 400
    if username in (None, "") or password in (None, ""):
        assert response.status_code == 400
    else:
        assert response.status_code == 401
        assert "detail" in response.data
