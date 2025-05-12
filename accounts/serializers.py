from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

from .models import Student, Lecturer, User

class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True, write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Student
        fields = ['matric_number', 'first_name', 'last_name', 'email', 'password']

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role='STUDENT'
        )

        student = Student.objects.create(user=user, **validated_data)
        return student


class LecturerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_null=True, write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Lecturer
        fields = ['staff_id', 'first_name', 'last_name', 'email', 'password']

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        email = validated_data.pop('email', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role='LECTURER'
        )

        lecturer = Lecturer.objects.create(user=user, **validated_data)
        return lecturer

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={
            'input_type': 'password'
        },
        write_only=True)
