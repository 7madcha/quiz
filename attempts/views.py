from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from quizzes.models import Choice, Quiz
from .models import Answer, QuizAttempt
from .stats import get_student_progress


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status='published')

    if request.method == 'POST':
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            status='submitted',
            submitted_at=timezone.now(),
        )

        total_score = 0

        for question in quiz.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            selected_choice = None
            is_correct = False
            question_score = 0

            if selected_choice_id:
                selected_choice = Choice.objects.filter(
                    id=selected_choice_id,
                    question=question,
                ).first()

                if selected_choice and selected_choice.is_correct:
                    is_correct = True
                    question_score = question.points or 0
                    total_score += question_score

            Answer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                user_answer=selected_choice.text if selected_choice else '',
                is_correct=is_correct,
                score=question_score,
            )

        attempt.score = total_score
        attempt.status = 'corrected'
        attempt.save()

        return redirect('attempts:quiz_result', attempt_id=attempt.id)

    return render(request, 'attempts/start_quiz.html', {
        'quiz': quiz,
    })


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'quiz__domain'),
        id=attempt_id,
        user=request.user,
    )

    answers = attempt.answers.select_related(
        'question',
        'selected_choice',
    )

    total_points = sum(
        (question.points or 0) for question in attempt.quiz.questions.all()
    )

    return render(request, 'attempts/quiz_result.html', {
        'attempt': attempt,
        'answers': answers,
        'total_points': total_points,
    })


@login_required
def my_results(request):
    attempts = QuizAttempt.objects.filter(
        user=request.user,
    ).select_related(
        'quiz',
        'quiz__domain',
    ).order_by('-submitted_at', '-started_at')

    return render(request, 'attempts/my_results.html', {
        'attempts': attempts,
    })


@login_required
def my_progress(request):
    return render(request, 'attempts/my_progress.html', get_student_progress(request.user))
