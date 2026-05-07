from django.core.exceptions import ObjectDoesNotExist


def role_flags(request):
    user = getattr(request, 'user', None)
    is_approved_teacher = False
    is_platform_admin = False
    is_student = False
    teacher_status = ''

    if user and user.is_authenticated:
        is_platform_admin = user.is_staff or user.is_superuser
        try:
            teacher_status = user.teacherprofile.status
            is_approved_teacher = teacher_status == 'approved'
        except ObjectDoesNotExist:
            teacher_status = ''
        is_student = not is_platform_admin and not is_approved_teacher

    return {
        'is_approved_teacher': is_approved_teacher,
        'is_platform_admin': is_platform_admin,
        'is_student': is_student,
        'teacher_status': teacher_status,
    }
