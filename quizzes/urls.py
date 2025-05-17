from django.urls import path

from . import views

urlpatterns = [
    path('', views.QuizCreateView.as_view(), name='quiz_create'),
    path('all/', views.QuizListView.as_view(), name='quiz_list'),
    path(
        'detail/<uuid:quiz_id>/',
        views.QuizDetailView.as_view(),
        name='quiz_detail',
    ),
    path(
        '<uuid:quiz_id>/questions/',
        views.QuestionCreateView.as_view(),
        name='question_create',
    ),
    path(
        '<uuid:quiz_id>/questions/<uuid:question_id>/',
        views.QuestionUpdateView.as_view(),
        name='question_update',
    ),
    path(
        '<uuid:quiz_id>/attempt/',
        views.AttemptQuizView.as_view(),
        name='quiz_attempt',
    ),
]
