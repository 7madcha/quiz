from quizzes.models import Choice, Question, Quiz


def create_fake_ai_quiz(*, user, subject, domain, difficulty, number_of_questions):
    quiz = Quiz.objects.create(
        title=f"AI Quiz about {subject}",
        subject=subject,
        domain=domain,
        difficulty=difficulty,
        created_by=user,
        is_ai_generated=True,
        status='pending',
    )

    for index in range(1, number_of_questions + 1):
        correct_text = f"Correct answer {index}"
        question = Question.objects.create(
            quiz=quiz,
            text=f"Fake AI question {index} about {subject}?",
            question_type='mcq',
            correct_answer=correct_text,
            explanation=f"This is a fake explanation for question {index}.",
            points=1,
        )

        Choice.objects.create(
            question=question,
            text=correct_text,
            is_correct=True,
        )

        for choice_index in range(1, 4):
            Choice.objects.create(
                question=question,
                text=f"Wrong answer {index}.{choice_index}",
                is_correct=False,
            )

    return quiz
