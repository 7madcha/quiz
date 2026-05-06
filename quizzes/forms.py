from django import forms

from .models import Choice, Question, Quiz


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'domain', 'difficulty', 'status']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'draft'

        if user and hasattr(user, 'teacherprofile') and user.teacherprofile.domain:
            self.fields['domain'].queryset = self.fields['domain'].queryset.filter(
                id=user.teacherprofile.domain_id
            )
            self.fields['domain'].initial = user.teacherprofile.domain


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'correct_answer', 'explanation', 'points']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
