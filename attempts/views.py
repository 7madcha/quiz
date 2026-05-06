from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from quizzes.models import Choice, Quiz
from .models import Answer, QuizAttempt


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
                    question_score = question.points
                    total_score += question.points

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
        question.points for question in attempt.quiz.questions.all()
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
    attempts = QuizAttempt.objects.filter(
        user=request.user,
        status="corrected",
    ).select_related(
        "quiz",
        "quiz__domain",
    ).prefetch_related(
        "quiz__questions",
    ).order_by("-submitted_at", "-started_at")

    progress_attempts = []

    total_percentage = 0
    best_percentage = 0

    domain_data = {}

    for attempt in attempts:
        questions = attempt.quiz.questions.all()
        total_points = sum(question.points for question in questions)

        if total_points > 0:
            percentage = round((attempt.score / total_points) * 100, 2)
        else:
            percentage = 0

        total_percentage += percentage

        if percentage > best_percentage:
            best_percentage = percentage

        domain_name = attempt.quiz.domain.name if attempt.quiz.domain else "No domain"

        if domain_name not in domain_data:
            domain_data[domain_name] = {
                "domain": domain_name,
                "attempts_count": 0,
                "total_percentage": 0,
            }

        domain_data[domain_name]["attempts_count"] += 1
        domain_data[domain_name]["total_percentage"] += percentage

        progress_attempts.append({
            "attempt": attempt,
            "quiz": attempt.quiz,
            "domain": domain_name,
            "score": attempt.score,
            "total_points": total_points,
            "percentage": percentage,
            "submitted_at": attempt.submitted_at,
        })

    total_attempts = len(progress_attempts)

    if total_attempts > 0:
        average_percentage = round(total_percentage / total_attempts, 2)
    else:
        average_percentage = 0

    domain_stats = []

    for domain_name, data in domain_data.items():
        attempts_count = data["attempts_count"]

        if attempts_count > 0:
            average = round(data["total_percentage"] / attempts_count, 2)
        else:
            average = 0

        domain_stats.append({
            "domain": domain_name,
            "attempts_count": attempts_count,
            "average_percentage": average,
        })

    domain_stats = sorted(
        domain_stats,
        key=lambda item: item["average_percentage"],
        reverse=True,
    )

    weak_domains = sorted(
        domain_stats,
        key=lambda item: item["average_percentage"],
    )[:3]

    last_5_attempts = progress_attempts[:5]

    return render(request, "attempts/my_progress.html", {
        "total_attempts": total_attempts,
        "average_percentage": average_percentage,
        "best_percentage": best_percentage,
        "last_5_attempts": last_5_attempts,
        "domain_stats": domain_stats,
        "weak_domains": weak_domains,
    })