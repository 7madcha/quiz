from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Domain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TeacherProfile(models.Model):
    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("approved", "Validé"),
        ("rejected", "Refusé"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    domains = models.ManyToManyField(Domain, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Profil enseignant - {self.user.username}"


class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Facile"),
        ("medium", "Moyen"),
        ("hard", "Difficile"),
    ]

    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("pending", "En attente de validation"),
        ("validated", "Validé"),
        ("published", "Publié"),
        ("rejected", "Refusé"),
        ("archived", "Archivé"),
    ]

    MODE_CHOICES = [
        ("training", "Quiz d'entraînement"),
        ("evaluation", "Quiz d'évaluation"),
        ("adaptive", "Quiz adaptatif"),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="training")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_points(self):
        return sum(question.points for question in self.questions.all())

    def __str__(self):
        return self.title


class Question(models.Model):
    QUESTION_TYPES = [
        ("mcq", "QCM"),
        ("true_false", "Vrai / Faux"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.text[:80]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "En cours"),
        ("submitted", "Soumis"),
        ("corrected", "Corrigé"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_progress")

    def percentage(self):
        total = self.quiz.total_points()
        if total == 0:
            return 0
        return round((self.score / total) * 100, 2)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"Réponse à {self.question.text[:50]}"