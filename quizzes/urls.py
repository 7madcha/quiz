from django.urls import path
from . import views

app_name = "quizzes"

urlpatterns = [
    path('teacher/my-quizzes/', views.teacher_quiz_list, name='teacher_quiz_list'),
    path('teacher/create/', views.teacher_create_quiz, name='teacher_create_quiz'),
    path('teacher/<int:quiz_id>/manage/', views.teacher_manage_quiz, name='teacher_manage_quiz'),
    path('teacher/<int:quiz_id>/add-question/', views.teacher_add_question, name='teacher_add_question'),
    path('teacher/question/<int:question_id>/add-choice/', views.teacher_add_choice, name='teacher_add_choice'),
    path('teacher/ai-pending/', views.teacher_ai_pending, name='teacher_ai_pending'),
    path('teacher/ai/<int:quiz_id>/review/', views.teacher_review_ai_quiz, name='teacher_review_ai_quiz'),
    path('teacher/ai/<int:quiz_id>/approve/', views.teacher_approve_ai_quiz, name='teacher_approve_ai_quiz'),
    path('teacher/ai/<int:quiz_id>/reject/', views.teacher_reject_ai_quiz, name='teacher_reject_ai_quiz'),
    path('', views.quiz_list, name='quiz_list'),
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
]
