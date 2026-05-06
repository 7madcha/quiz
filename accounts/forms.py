from django.contrib.auth.forms import UserCreationForm
from django import forms

from quizzes.models import Domain
from .models import TeacherProfile


class TeacherRegistrationForm(UserCreationForm):
    domain = forms.ModelChoiceField(
        queryset=Domain.objects.all(),
        required=False,
        help_text="Optional teaching domain.",
    )

    def save(self, commit=True):
        user = super().save(commit=commit)

        if commit:
            TeacherProfile.objects.create(
                user=user,
                domain=self.cleaned_data.get('domain'),
                status='pending',
            )

        return user
