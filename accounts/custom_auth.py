from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import Student, Lecturer

User = get_user_model()

class AcadexAuthBackend(ModelBackend):
    """
    Custom authentication backend to authenticate users
    with either matric/password for students or staff-id/password for lectures.
    """

    def authenticate(self, request, username = ..., password = ..., **kwargs):
        """
        Authenticate a user based on the username and password.
        The username can be either a matric number (for students) or a staff ID (for teachers).
        """
        if not username or not password:
            return None

        try:
            student = Student.objects.get(matric_number=username)
            user = student.user
            if user.check_password(password):
                return user
        except Student.DoesNotExist:
            pass

        try:
            lecturer = Lecturer.objects.get(staff_id=username)
            user = lecturer.user
            if user.check_password(password):
                return user
        except Lecturer.DoesNotExist:
            pass

        return None

acadex_auth = AcadexAuthBackend()
