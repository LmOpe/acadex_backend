from django.urls import path

from . import views

urlpatterns = [
    path('', views.QuizCreateView.as_view(), name='quiz_create'),
    path('all/', views.QuizListView.as_view(), name='quiz_list'),
]
