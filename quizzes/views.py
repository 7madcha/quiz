
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import TeacherProfile
from .forms import ChoiceForm, QuestionForm, QuizForm
from .models import Question, Quiz


def user_is_approved_teacher(user):
    try:
        return user.is_authenticated and user.teacherprofile.status == 'approved'
    except TeacherProfile.DoesNotExist:
        return False


def teacher_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not user_is_approved_teacher(request.user):
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


def home(request):
    return render(request, 'home.html')


def quiz_list(request):
    quizzes = Quiz.objects.filter(status='published')
    return render(request, 'quizzes/quiz_list.html', {'quizzes': quizzes})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quizzes/quiz_detail.html', {'quiz': quiz})


@teacher_required
def teacher_quiz_list(request):
    quizzes = Quiz.objects.filter(
        created_by=request.user
    ).select_related('domain').order_by('-created_at')

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
            quiz.save()
            return redirect('quizzes:teacher_manage_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm(user=request.user)

    return render(request, 'quizzes/teacher_create_quiz.html', {
        'form': form,
    })


@teacher_required
def teacher_manage_quiz(request, quiz_id):
    quiz = get_object_or_404(
        Quiz.objects.select_related('domain').prefetch_related(
            'questions',
            'questions__choices',
        ),
        id=quiz_id,
        created_by=request.user,
    )

    return render(request, 'quizzes/teacher_manage_quiz.html', {
        'quiz': quiz,
    })


@teacher_required
def teacher_add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
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
        quiz__created_by=request.user,
    )

    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('quizzes:teacher_manage_quiz', quiz_id=question.quiz.id)
    else:
        form = ChoiceForm()

    return render(request, 'quizzes/teacher_add_choice.html', {
        'form': form,
        'question': question,
    })


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
    messages.success(request, 'AI quiz approved.')
    return redirect('quizzes:teacher_ai_pending')


@teacher_required
@require_POST
def teacher_reject_ai_quiz(request, quiz_id):
    quiz = get_teacher_pending_ai_quiz(request.user, quiz_id)
    quiz.status = 'rejected'
    quiz.save(update_fields=['status'])
    messages.success(request, 'AI quiz rejected.')
    return redirect('quizzes:teacher_ai_pending')
