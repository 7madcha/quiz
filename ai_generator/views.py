from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import FakeAIQuizForm
from .services import generate_quiz_with_groq


@login_required
def generate_quiz_view(request):
    if request.method == 'POST':
        form = FakeAIQuizForm(request.POST)
        if form.is_valid():
            success, quiz, error_message = generate_quiz_with_groq(
                subject=form.cleaned_data['subject'],
                domain=form.cleaned_data['domain'],
                difficulty=form.cleaned_data['difficulty'],
                number_of_questions=form.cleaned_data['number_of_questions'],
                created_by=request.user,
            )
            if success:
                messages.success(request, 'AI quiz generated with Groq and sent for teacher validation.')
                return redirect('ai_generator:generated_success', quiz_id=quiz.id)
            messages.error(request, error_message)
    else:
        form = FakeAIQuizForm()

    return render(request, 'ai_generator/generate_quiz.html', {
        'form': form,
    })


@login_required
def generated_success_view(request, quiz_id):
    return render(request, 'ai_generator/generated_success.html', {
        'quiz_id': quiz_id,
    })
