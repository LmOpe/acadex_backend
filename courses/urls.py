from django.urls import path

from . import views

urlpatterns = [
    path('', views.CourseListCreateView.as_view(), name='course_list_create'),
    path('<str:course_id>/enroll/', views.CourseEnrollmentView.as_view(), name='course_enroll'),
    path('students/enrollments/', views.StudentEnrollmentsView.as_view(), name='student_enrollments'),
]
