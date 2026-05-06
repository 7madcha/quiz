

# Create your views here.
from django.shortcuts import render, get_object_or_404
from quizzes.models import Quiz


def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'attempts/start_quiz.html', {'quiz': quiz})