from django.contrib import admin


from .models import Domain, Quiz, Question, Choice
# Register your models here
admin.site.register(Domain)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)