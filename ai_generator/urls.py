from django.urls import path
from . import views

app_name = "ai_generator"

urlpatterns = [
    path('generate/', views.generate_quiz_view, name='generate_quiz'),
    path('generated/<int:quiz_id>/', views.generated_success_view, name='generated_success'),
]
