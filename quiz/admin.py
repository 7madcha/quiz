from django.contrib import admin



from .models import Domain, TeacherProfile, Quiz, Question, Choice, QuizAttempt, Answer
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "status")
    filter_horizontal = ("domains",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "domain", "difficulty", "mode", "status", "is_ai_generated")
    list_filter = ("status", "difficulty", "mode", "domain", "is_ai_generated")
    search_fields = ("title", "subject")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "question_type", "points")
    list_filter = ("question_type",)
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "status", "started_at", "submitted_at")
    list_filter = ("status",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_choice", "is_correct", "score")