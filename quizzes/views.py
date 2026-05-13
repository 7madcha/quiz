from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import TeacherProfile
from attempts.models import QuizAttempt
from .forms import ChoiceForm, QuestionForm, QuizForm
from .models import Choice, Question, Quiz


def user_is_approved_teacher(user):
    try:
        return user.is_authenticated and user.teacherprofile.status == 'approved'
    except TeacherProfile.DoesNotExist:
        return False


def teacher_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not user_is_approved_teacher(request.user):
            messages.error(request, 'You need an approved teacher account to access that page.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)

    return wrapper


def get_teacher_pending_ai_quiz(user, quiz_id):
    return get_object_or_404(
        Quiz.objects.select_related('domain').prefetch_related(
            'questions',
            'questions__choices',
        ),
        id=quiz_id,
        is_ai_generated=True,
        status='pending',
        domain=user.teacherprofile.domain,
    )


def get_teacher_manageable_quizzes(user):
    return Quiz.objects.filter(
        Q(created_by=user) |
        Q(
            is_ai_generated=True,
            domain=user.teacherprofile.domain,
            status__in=['approved', 'published'],
        )
    )


def get_teacher_domain_quizzes(user):
    return Quiz.objects.filter(domain=user.teacherprofile.domain)


def get_quiz_publish_issues(quiz):
    questions = list(quiz.questions.all())
    issues = []

    if not questions:
        issues.append('Add at least one question before publishing.')
        return issues

    for question in questions:
        choices = list(question.choices.all())

        if not choices:
            issues.append(f'Question "{question.text[:80]}" has no choices.')
            continue

        if not any(choice.is_correct for choice in choices):
            issues.append(f'Question "{question.text[:80]}" has no correct choice.')

    return issues


def home(request):
    return render(request, 'home.html')


def quiz_list(request):
    quizzes = Quiz.objects.filter(status='published')
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status='published')
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})


@teacher_required
def teacher_quiz_list(request):
    quizzes = get_teacher_domain_quizzes(request.user).select_related(
        'domain',
        'created_by',
    ).annotate(
        attempts_count=Count('quizattempt'),
    ).order_by('-created_at')

    manageable_ids = set(
        get_teacher_manageable_quizzes(request.user).values_list('id', flat=True)
    )
    for quiz in quizzes:
        quiz.can_manage = quiz.id in manageable_ids

    return render(request, 'quizzes/teacher_quiz_list.html', {
        'quizzes': quizzes,
    })


@teacher_required
def teacher_create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.is_ai_generated = False
            quiz.status = 'draft'
            quiz.save()
            messages.success(request, 'Quiz created. Add questions and choices before publishing.')
            return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(user=request.user)

    return render(request, 'quizzes/teacher_create_quiz.html', {
        'form': form,
    })


@teacher_required
def teacher_manage_quiz(request, quiz_id):
    quiz = get_object_or_404(
        get_teacher_manageable_quizzes(request.user).select_related('domain', 'created_by').prefetch_related(
            'questions',
            'questions__choices',
        ),
        id=quiz_id,
    )

    return render(request, 'quizzes/teacher_manage_quiz.html', {
        'quiz': quiz,
        'publish_issues': get_quiz_publish_issues(quiz),
    })


@teacher_required
def teacher_quiz_results(request, quiz_id):
    quiz = get_object_or_404(
        get_teacher_domain_quizzes(request.user).select_related('domain').prefetch_related('questions'),
        id=quiz_id,
    )
    total_points = sum((question.points or 0) for question in quiz.questions.all())
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
    ).select_related(
        'user',
    ).prefetch_related(
        'answers',
        'answers__question',
        'answers__selected_choice',
    ).order_by('-submitted_at', '-started_at')

    attempt_rows = []
    total_percentage = 0
    best_percentage = 0

    for attempt in attempts:
        score = attempt.score or 0
        percentage = round((score / total_points) * 100, 2) if total_points else 0
        total_percentage += percentage
        best_percentage = max(best_percentage, percentage)
        attempt_rows.append({
            'attempt': attempt,
            'answers': attempt.answers.all(),
            'total_points': total_points,
            'percentage': percentage,
        })

    total_attempts = len(attempt_rows)
    average_percentage = round(total_percentage / total_attempts, 2) if total_attempts else 0

    return render(request, 'quizzes/teacher_quiz_results.html', {
        'quiz': quiz,
        'attempt_rows': attempt_rows,
        'total_attempts': total_attempts,
        'average_percentage': average_percentage,
        'best_percentage': best_percentage,
        'total_points': total_points,
    })


@teacher_required
@require_POST
def teacher_publish_quiz(request, quiz_id):
    quiz = get_object_or_404(
        get_teacher_manageable_quizzes(request.user).prefetch_related('questions', 'questions__choices'),
        id=quiz_id,
    )

    if quiz.status not in ['draft', 'approved']:
        messages.error(request, 'Only draft or approved quizzes can be published.')
        return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)

    publish_issues = get_quiz_publish_issues(quiz)
    if publish_issues:
        messages.error(request, publish_issues[0])
        return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)

    quiz.status = 'published'
    quiz.save(update_fields=['status'])
    messages.success(request, 'Quiz published.')
    return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)


@teacher_required
@require_POST
def teacher_unpublish_quiz(request, quiz_id):
    quiz = get_object_or_404(get_teacher_manageable_quizzes(request.user), id=quiz_id)

    if quiz.status != 'published':
        messages.error(request, 'Only published quizzes can be unpublished.')
        return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)

    quiz.status = 'approved' if quiz.is_ai_generated else 'draft'
    quiz.save(update_fields=['status'])
    messages.success(request, 'Quiz unpublished.')
    return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)


@teacher_required
def teacher_add_question(request, quiz_id):
    quiz = get_object_or_404(get_teacher_manageable_quizzes(request.user), id=quiz_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added.')
            return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)
    else:
        form = QuestionForm()

    return render(request, 'quizzes/teacher_add_question.html', {
        'form': form,
        'quiz': quiz,
    })


@teacher_required
def teacher_add_choice(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related('quiz'),
        id=question_id,
        quiz__in=get_teacher_manageable_quizzes(request.user),
    )

    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            messages.success(request, 'Choice added.')
            return redirect('quizzes:teacher_manage_quiz', quiz_id=question.quiz.id)
    else:
        form = ChoiceForm()

    return render(request, 'quizzes/teacher_add_choice.html', {
        'form': form,
        'question': question,
    })


@teacher_required
def teacher_edit_choice(request, choice_id):
    choice = get_object_or_404(
        Choice.objects.select_related('question', 'question__quiz'),
        id=choice_id,
        question__quiz__in=get_teacher_manageable_quizzes(request.user),
    )

    if request.method == 'POST':
        form = ChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Choice updated.')
            return redirect('quizzes:teacher_manage_quiz', quiz_id=choice.question.quiz.id)
    else:
        form = ChoiceForm(instance=choice)

    return render(request, 'quizzes/teacher_add_choice.html', {
        'form': form,
        'question': choice.question,
        'choice': choice,
        'is_edit': True,
    })


@teacher_required
@require_POST
def teacher_delete_choice(request, choice_id):
    choice = get_object_or_404(
        Choice.objects.select_related('question', 'question__quiz'),
        id=choice_id,
        question__quiz__in=get_teacher_manageable_quizzes(request.user),
    )
    quiz_id = choice.question.quiz.id
    choice.delete()
    messages.success(request, 'Choice deleted.')
    return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz_id)


@teacher_required
def teacher_ai_pending(request):
    quizzes = Quiz.objects.filter(
        is_ai_generated=True,
        status='pending',
        domain=request.user.teacherprofile.domain,
    ).select_related('domain', 'created_by').order_by('-created_at')

    return render(request, 'quizzes/teacher_ai_pending.html', {
        'quizzes': quizzes,
    })


@teacher_required
def teacher_review_ai_quiz(request, quiz_id):
    quiz = get_teacher_pending_ai_quiz(request.user, quiz_id)

    return render(request, 'quizzes/teacher_review_ai_quiz.html', {
        'quiz': quiz,
    })


@teacher_required
@require_POST
def teacher_approve_ai_quiz(request, quiz_id):
    quiz = get_teacher_pending_ai_quiz(request.user, quiz_id)
    quiz.status = 'approved'
    quiz.save(update_fields=['status'])
    messages.success(request, 'AI quiz approved. Publish it when it is ready for students.')
    return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)


@teacher_required
@require_POST
def teacher_reject_ai_quiz(request, quiz_id):
    quiz = get_teacher_pending_ai_quiz(request.user, quiz_id)
    quiz.status = 'rejected'
    quiz.save(update_fields=['status'])
    messages.success(request, 'AI quiz rejected.')
    return redirect('quizzes:teacher_ai_pending')
