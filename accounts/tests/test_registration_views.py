# tests/test_registration_views.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_student_registration_view_success(api_client):
    url = reverse('student_register')
    data = {
        "matric_number": "MAT202020",
        "first_name": "Test",
        "last_name": "Student",
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['matric_number'] == data['matric_number']

@pytest.mark.django_db
def test_student_registration_view_fail_missing_fields(api_client):
    url = reverse('student_register')
    data = {
        "matric_number": "MAT202020",
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 400
    assert "first_name" in response.data
    assert "last_name" in response.data

@pytest.mark.django_db
def test_lecturer_registration_view_success(api_client):
    url = reverse('lecturer_register')
    data = {
        "staff_id": "STF202020",
        "first_name": "Test",
        "last_name": "Lecturer",
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 201
    assert response.data['staff_id'] == data['staff_id']

@pytest.mark.django_db
def test_lecturer_registration_view_fail_missing_fields(api_client):
    url = reverse('lecturer_register')
    data = {
        "staff_id": "STF202020",
        "password": "testpass123"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == 400
    assert "first_name" in response.data
    assert "last_name" in response.data
