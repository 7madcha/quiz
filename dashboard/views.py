
# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import TeacherProfile
from attempts.models import QuizAttempt
from attempts.stats import get_student_progress
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
    progress = get_student_progress(request.user)

    return render(request, 'dashboard/learner_dashboard.html', {
        'attempts': attempts,
        'progress': progress,
    })


@login_required
def teacher_dashboard(request):
    if not is_approved_teacher(request.user):
        messages.error(request, 'You need an approved teacher account to access the teacher dashboard.')
        return redirect('dashboard:learner_dashboard')

    quizzes = Quiz.objects.filter(
        domain=request.user.teacherprofile.domain,
    ).select_related('domain').order_by('-created_at')[:10]

    manageable_ids = set(
        Quiz.objects.filter(
            Q(created_by=request.user) |
            Q(
                is_ai_generated=True,
                domain=request.user.teacherprofile.domain,
                status__in=['approved', 'published'],
            )
        ).values_list('id', flat=True)
    )
    for quiz in quizzes:
        quiz.can_manage = quiz.id in manageable_ids

    return render(request, 'dashboard/teacher_dashboard.html', {
        'quizzes': quizzes,
    })


@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You need an admin account to access the admin dashboard.')
        return redirect('dashboard:learner_dashboard')

    total_quizzes = Quiz.objects.count()
    published_quizzes = Quiz.objects.filter(status='published').count()
    total_attempts = QuizAttempt.objects.count()
    pending_teachers = TeacherProfile.objects.filter(
        status='pending',
    ).select_related('user', 'domain').order_by('user__username')
    approved_teachers = TeacherProfile.objects.filter(
        status='approved',
    ).select_related('user', 'domain').order_by('user__username')[:5]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_quizzes': total_quizzes,
        'published_quizzes': published_quizzes,
        'total_attempts': total_attempts,
        'pending_teachers': pending_teachers,
        'approved_teachers': approved_teachers,
    })


@login_required
@require_POST
def approve_teacher(request, profile_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You need an admin account to approve teachers.')
        return redirect('dashboard:home')

    profile = get_object_or_404(TeacherProfile, id=profile_id)
    profile.status = 'approved'
    profile.save(update_fields=['status'])
    messages.success(request, f'{profile.user.username} is now an approved teacher.')
    return redirect('dashboard:admin_dashboard')


@login_required
@require_POST
def reject_teacher(request, profile_id):
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You need an admin account to reject teachers.')
        return redirect('dashboard:home')

    profile = get_object_or_404(TeacherProfile, id=profile_id)
    profile.status = 'rejected'
    profile.save(update_fields=['status'])
    messages.success(request, f'{profile.user.username} teacher request rejected.')
    return redirect('dashboard:admin_dashboard')
