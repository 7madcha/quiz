from django.core.exceptions import ObjectDoesNotExist


def role_flags(request):
    user = getattr(request, 'user', None)
    is_approved_teacher = False
    teacher_status = ''

    if user and user.is_authenticated:
        try:
            teacher_status = user.teacherprofile.status
            is_approved_teacher = teacher_status == 'approved'
        except ObjectDoesNotExist:
            teacher_status = ''

    return {
        'is_approved_teacher': is_approved_teacher,
        'teacher_status': teacher_status,
    }
