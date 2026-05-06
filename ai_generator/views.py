from django.shortcuts import render

# Create your views here.



def generate_quiz_view(request):
    return render(request, 'ai_generator/generate_quiz.html')