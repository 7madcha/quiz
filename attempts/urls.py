from django.urls import path
from . import views

app_name = "attempts"

urlpatterns = [
    path('start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('my-results/', views.my_results, name='my_results'),
]