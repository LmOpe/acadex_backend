from django.urls import path

from . import views

urlpatterns = [
    path('', views.QuizCreateView.as_view(), name='quiz_create'),
]
