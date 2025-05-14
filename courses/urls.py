from django.urls import path

from . import views

urlpatterns = [
    path('', views.CourseListCreateView.as_view(), name='course_list_create'),
    # path('courses/<str:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('<str:course_id>/enroll/', views.CourseEnrollmentView.as_view(), name='course_enroll'),
]