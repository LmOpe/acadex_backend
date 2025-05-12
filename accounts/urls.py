from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('student/register/', views.StudentRegistrationView.as_view(), name='student_register'),
    path('lecturer/register/', views.LecturerRegistrationView.as_view(), name='lecturer_register'),
    path('token/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
