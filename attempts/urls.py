from django.urls import path
from . import views

app_name = "attempts"

urlpatterns = [
    path('start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
]