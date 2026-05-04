from django.contrib import admin



from .models import QuizAttempt, Answer
# Register your models here.
admin.site.register(QuizAttempt)
admin.site.register(Answer)