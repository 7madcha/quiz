from django import forms

from quizzes.models import Domain, Quiz


class FakeAIQuizForm(forms.Form):
    subject = forms.CharField(max_length=200)
    domain = forms.ModelChoiceField(queryset=Domain.objects.all())
    difficulty = forms.ChoiceField(choices=Quiz.DIFFICULTY_CHOICES)
    number_of_questions = forms.IntegerField(min_value=1, max_value=20, initial=5)
