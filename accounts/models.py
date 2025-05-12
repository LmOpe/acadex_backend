from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not first_name or not last_name:
            raise ValueError('The First Name and Last Name fields must be set')
        user = self.model(first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(first_name, last_name, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('LECTURER', 'Lecturer'),
        ('ADMIN', 'Admin'),
    )

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    matric_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.matric_number}"

class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.staff_id}"
