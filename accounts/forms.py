from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction

from quizzes.models import Domain
from .models import TeacherProfile


class RegistrationForm(UserCreationForm):
    request_teacher = forms.BooleanField(
        required=False,
        label="I want to register as a teacher",
        help_text="Teacher accounts need admin approval before teacher features are available.",
    )
    domain = forms.ModelChoiceField(
        queryset=Domain.objects.all(),
        required=False,
        help_text="Optional teaching domain.",
    )

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=commit)

            if commit and self.cleaned_data.get('request_teacher'):
                TeacherProfile.objects.create(
                    user=user,
                    domain=self.cleaned_data.get('domain'),
                    status='pending',
                )

        return user
