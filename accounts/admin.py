from django.contrib import admin


from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'domain', 'status')
    list_filter = ('status', 'domain')
    search_fields = ('user__username', 'user__email', 'domain__name')
    actions = ('approve_teachers', 'reject_teachers')

    @admin.action(description='Approve selected teachers')
    def approve_teachers(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected teachers')
    def reject_teachers(self, request, queryset):
        queryset.update(status='rejected')
