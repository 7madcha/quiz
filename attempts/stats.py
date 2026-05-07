from .models import QuizAttempt


def get_student_progress(user):
    attempts = QuizAttempt.objects.filter(
        user=user,
        status='corrected',
    ).select_related(
        'quiz',
        'quiz__domain',
    ).prefetch_related(
        'quiz__questions',
    ).order_by('-submitted_at', '-started_at')

    progress_attempts = []
    total_percentage = 0
    best_percentage = 0
    domain_data = {}

    for attempt in attempts:
        quiz = attempt.quiz
        questions = list(quiz.questions.all()) if quiz else []
        total_points = sum((question.points or 0) for question in questions)
        score = attempt.score or 0

        percentage = round((score / total_points) * 100, 2) if total_points > 0 else 0
        total_percentage += percentage
        best_percentage = max(best_percentage, percentage)

        domain = getattr(quiz, 'domain', None)
        domain_name = getattr(domain, 'name', None) or 'No domain'

        if domain_name not in domain_data:
            domain_data[domain_name] = {
                'domain': domain_name,
                'attempts_count': 0,
                'total_percentage': 0,
            }

        domain_data[domain_name]['attempts_count'] += 1
        domain_data[domain_name]['total_percentage'] += percentage

        progress_attempts.append({
            'attempt': attempt,
            'quiz': quiz,
            'domain': domain_name,
            'score': score,
            'total_points': total_points,
            'percentage': percentage,
            'submitted_at': attempt.submitted_at,
        })

    total_attempts = len(progress_attempts)
    average_percentage = round(total_percentage / total_attempts, 2) if total_attempts else 0

    domain_stats = []
    for data in domain_data.values():
        attempts_count = data['attempts_count']
        average = round(data['total_percentage'] / attempts_count, 2) if attempts_count else 0
        domain_stats.append({
            'domain': data['domain'],
            'attempts_count': attempts_count,
            'average_percentage': average,
        })

    domain_stats = sorted(
        domain_stats,
        key=lambda item: item['average_percentage'],
        reverse=True,
    )

    return {
        'total_attempts': total_attempts,
        'average_percentage': average_percentage,
        'best_percentage': best_percentage,
        'last_5_attempts': progress_attempts[:5],
        'domain_stats': domain_stats,
        'weak_domains': sorted(domain_stats, key=lambda item: item['average_percentage'])[:3],
    }
