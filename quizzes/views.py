


from django.shortcuts import render, get_object_or_404
from .models import Quiz


def home(request):
    return render(request, 'home.html')


def quiz_list(request):
    quizzes = Quiz.objects.filter(status='published')
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})