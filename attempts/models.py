from django.db import models



from django.contrib.auth.models import User
# Create your models here.

class QuizAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In progress'),
        ('submitted', 'Submitted'),
        ('corrected', 'Corrected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('quizzes.Question', on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        'quizzes.Choice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    user_answer = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"Answer by {self.attempt.user.username}"