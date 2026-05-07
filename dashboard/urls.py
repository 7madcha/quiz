from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('learner/', views.learner_dashboard, name='learner_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/teachers/<int:profile_id>/approve/', views.approve_teacher, name='approve_teacher'),
    path('admin-dashboard/teachers/<int:profile_id>/reject/', views.reject_teacher, name='reject_teacher'),
]
