from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import TeacherProfile
from attempts.models import Answer, QuizAttempt
from .models import Choice, Domain, Question, Quiz


class TeacherDomainQuizTests(TestCase):
    def setUp(self):
        self.domain = Domain.objects.create(name='Math')
        self.other_domain = Domain.objects.create(name='Physics')
        self.teacher = User.objects.create_user(username='teacher', password='pass12345')
        TeacherProfile.objects.create(
            user=self.teacher,
            domain=self.domain,
            status='approved',
        )

    def test_teacher_list_shows_all_quizzes_in_domain(self):
        Quiz.objects.create(
            title='Teacher quiz',
            subject='Algebra',
            domain=self.domain,
            difficulty='easy',
            created_by=self.teacher,
        )
        Quiz.objects.create(
            title='Other teacher same domain',
            subject='Geometry',
            domain=self.domain,
            difficulty='medium',
        )
        Quiz.objects.create(
            title='Other domain quiz',
            subject='Forces',
            domain=self.other_domain,
            difficulty='hard',
        )

        self.client.login(username='teacher', password='pass12345')
        response = self.client.get(reverse('quizzes:teacher_quiz_list'))

        self.assertContains(response, 'Teacher quiz')
        self.assertContains(response, 'Other teacher same domain')
        self.assertNotContains(response, 'Other domain quiz')

    def test_teacher_can_view_student_answers_for_domain_quiz(self):
        quiz = Quiz.objects.create(
            title='Fractions',
            subject='Math',
            domain=self.domain,
            difficulty='easy',
            status='published',
        )
        question = Question.objects.create(
            quiz=quiz,
            text='1/2 + 1/2?',
            question_type='mcq',
            correct_answer='1',
            points=1,
        )
        choice = Choice.objects.create(question=question, text='1', is_correct=True)
        student = User.objects.create_user(username='student', password='pass12345')
        attempt = QuizAttempt.objects.create(
            user=student,
            quiz=quiz,
            score=1,
            status='corrected',
        )
        Answer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=choice,
            user_answer='1',
            is_correct=True,
            score=1,
        )

        self.client.login(username='teacher', password='pass12345')
        response = self.client.get(reverse('quizzes:teacher_quiz_results', args=[quiz.id]))

        self.assertContains(response, 'student')
        self.assertContains(response, '1/2 + 1/2?')
        self.assertContains(response, 'Correct')

    def test_teacher_cannot_view_results_for_other_domain_quiz(self):
        quiz = Quiz.objects.create(
            title='Forces',
            subject='Physics',
            domain=self.other_domain,
            difficulty='medium',
        )

        self.client.login(username='teacher', password='pass12345')
        response = self.client.get(reverse('quizzes:teacher_quiz_results', args=[quiz.id]))

        self.assertEqual(response.status_code, 404)

    def test_teacher_can_edit_choice_for_manageable_quiz(self):
        quiz = Quiz.objects.create(
            title='Teacher quiz',
            subject='Algebra',
            domain=self.domain,
            difficulty='easy',
            created_by=self.teacher,
        )
        question = Question.objects.create(
            quiz=quiz,
            text='2 + 2?',
            question_type='mcq',
            correct_answer='4',
            points=1,
        )
        choice = Choice.objects.create(question=question, text='3', is_correct=False)

        self.client.login(username='teacher', password='pass12345')
        response = self.client.post(
            reverse('quizzes:teacher_edit_choice', args=[choice.id]),
            {'text': '4', 'is_correct': 'on'},
        )
        choice.refresh_from_db()

        self.assertRedirects(response, reverse('quizzes:teacher_manage_quiz', args=[quiz.id]))
        self.assertEqual(choice.text, '4')
        self.assertTrue(choice.is_correct)

    def test_teacher_can_delete_choice_for_manageable_quiz(self):
        quiz = Quiz.objects.create(
            title='Teacher quiz',
            subject='Algebra',
            domain=self.domain,
            difficulty='easy',
            created_by=self.teacher,
        )
        question = Question.objects.create(
            quiz=quiz,
            text='2 + 2?',
            question_type='mcq',
            correct_answer='4',
            points=1,
        )
        choice = Choice.objects.create(question=question, text='4', is_correct=True)

        self.client.login(username='teacher', password='pass12345')
        response = self.client.post(reverse('quizzes:teacher_delete_choice', args=[choice.id]))

        self.assertRedirects(response, reverse('quizzes:teacher_manage_quiz', args=[quiz.id]))
        self.assertFalse(Choice.objects.filter(id=choice.id).exists())
