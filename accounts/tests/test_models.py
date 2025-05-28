import pytest
from accounts.models import User, Student, Lecturer

@pytest.mark.django_db
def test_create_user_and_superuser():
    # Create a normal user
    user = User.objects.create_user(first_name='John', last_name='Doe', password='pass1234')
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.check_password('pass1234')
    assert not user.is_staff
    assert not user.is_superuser

    # Create a superuser
    superuser = User.objects.create_superuser(first_name='Admin', last_name='User', password='pass1234')
    assert superuser.is_staff
    assert superuser.is_superuser
    assert superuser.check_password('pass1234')

@pytest.mark.django_db
def test_user_str_method():
    user = User.objects.create_user(first_name='Jane', last_name='Smith', password='pass1234')
    assert str(user) == "Jane Smith"

@pytest.mark.django_db
def test_student_str_method():
    user = User.objects.create_user(first_name='Alice', last_name='Jones', password='pass1234')
    student = Student.objects.create(user=user, matric_number='MAT123456')
    assert str(student) == "Alice Jones - MAT123456"

@pytest.mark.django_db
def test_lecturer_str_method():
    user = User.objects.create_user(first_name='Bob', last_name='Brown', password='pass1234')
    lecturer = Lecturer.objects.create(user=user, staff_id='STF654321')
    assert str(lecturer) == "Bob Brown - STF654321"

def test_create_user_missing_first_or_last_name_raises():
    # Missing first_name
    with pytest.raises(ValueError, match='The First Name and Last Name fields must be set'):
        User.objects.create_user(first_name='', last_name='Smith', password='pass1234')

    # Missing last_name
    with pytest.raises(ValueError, match='The First Name and Last Name fields must be set'):
        User.objects.create_user(first_name='John', last_name='', password='pass1234')

    # Both missing
    with pytest.raises(ValueError, match='The First Name and Last Name fields must be set'):
        User.objects.create_user(first_name=None, last_name=None, password='pass1234')
