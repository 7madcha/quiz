
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import TeacherProfile
from attempts.models import QuizAttempt
from quizzes.models import Quiz


def is_approved_teacher(user):
    try:
        return user.teacherprofile.status == 'approved'
    except TeacherProfile.DoesNotExist:
        return False


@login_required
def dashboard_home(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')

    if is_approved_teacher(request.user):
        return redirect('dashboard:teacher_dashboard')

    return redirect('dashboard:learner_dashboard')


@login_required
def learner_dashboard(request):
    attempts = QuizAttempt.objects.filter(
        user=request.user
    ).select_related('quiz').order_by('-started_at')[:5]

    return render(request, 'dashboard/learner_dashboard.html', {
        'attempts': attempts,
    })


@login_required
def teacher_dashboard(request):
    if not is_approved_teacher(request.user):
        return redirect('dashboard:learner_dashboard')

    quizzes = Quiz.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]

    return render(request, 'dashboard/teacher_dashboard.html', {
        'quizzes': quizzes,
    })


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard:learner_dashboard')

    total_quizzes = Quiz.objects.count()
    published_quizzes = Quiz.objects.filter(status='published').count()
    total_attempts = QuizAttempt.objects.count()

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_quizzes': total_quizzes,
        'published_quizzes': published_quizzes,
        'total_attempts': total_attempts,
    })
