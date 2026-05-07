import json
import os

from django.db import transaction

from .prompts import build_groq_quiz_prompt
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


def generate_quiz_with_groq(*, subject, domain, difficulty, number_of_questions, created_by):
    subject = clean_text(subject)
    try:
        number_of_questions = int(number_of_questions)
    except (TypeError, ValueError):
        return False, None, 'Number of questions must be a valid number.'

    input_error = validate_generation_input(
        subject=subject,
        domain=domain,
        difficulty=difficulty,
        number_of_questions=number_of_questions,
    )
    if input_error:
        return False, None, input_error

    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return False, None, 'Groq API key is not configured.'

    try:
        from groq import Groq
    except ImportError:
        return False, None, 'Groq SDK is not installed. Run pip install groq.'

    prompt = build_groq_quiz_prompt(
        subject=subject,
        domain=domain,
        difficulty=difficulty,
        number_of_questions=number_of_questions,
    )

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=[
                {
                    'role': 'system',
                    'content': 'You generate educational quizzes and return strict JSON only.',
                },
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            temperature=0.3,
        )
        content = completion.choices[0].message.content
    except Exception:
        return False, None, 'Groq could not generate a quiz. Please try again.'

    try:
        payload = json.loads(normalize_json_text(content))
    except (TypeError, json.JSONDecodeError):
        return False, None, 'Groq returned invalid quiz data. Please try again.'

    success, validated, error = validate_groq_quiz_payload(
        payload,
        subject=subject,
        number_of_questions=number_of_questions,
    )
    if not success:
        return False, None, error

    with transaction.atomic():
        quiz = Quiz.objects.create(
            title=validated['title'],
            subject=subject,
            domain=domain,
            difficulty=difficulty,
            created_by=created_by,
            is_ai_generated=True,
            status='pending',
        )

        for item in validated['questions']:
            question = Question.objects.create(
                quiz=quiz,
                text=item['text'],
                question_type='mcq',
                correct_answer=item['correct_answer'],
                explanation=item['explanation'],
                points=1,
            )

            for choice in item['choices']:
                Choice.objects.create(
                    question=question,
                    text=choice['text'],
                    is_correct=choice['is_correct'],
                )

    return True, quiz, ''


def validate_generation_input(*, subject, domain, difficulty, number_of_questions):
    valid_difficulties = {choice[0] for choice in Quiz.DIFFICULTY_CHOICES}

    if not subject:
        return 'Subject is required.'
    if not domain:
        return 'Domain is required.'
    if difficulty not in valid_difficulties:
        return 'Difficulty is invalid.'
    if number_of_questions < 1 or number_of_questions > 10:
        return 'Number of questions must be between 1 and 10.'
    return ''


def validate_groq_quiz_payload(payload, *, subject, number_of_questions):
    if not isinstance(payload, dict):
        return False, None, 'Groq returned invalid quiz data. Please try again.'

    title = clean_text(payload.get('title')) or f'AI Quiz about {subject}'
    questions = payload.get('questions')

    if not isinstance(questions, list) or len(questions) != number_of_questions:
        return False, None, 'Groq returned the wrong number of questions. Please try again.'

    validated_questions = []
    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            return False, None, f'Question {index} is invalid. Please try again.'

        text = clean_text(question.get('text'))
        correct_answer = clean_text(question.get('correct_answer'))
        explanation = clean_text(question.get('explanation'))
        choices = question.get('choices')

        if not text:
            return False, None, f'Question {index} has no text. Please try again.'
        if not correct_answer:
            return False, None, f'Question {index} has no correct answer. Please try again.'
        if not explanation:
            return False, None, f'Question {index} has no explanation. Please try again.'
        if not isinstance(choices, list) or len(choices) != 4:
            return False, None, f'Question {index} must have exactly 4 choices. Please try again.'

        validated_choices = []
        correct_choices = []
        for choice_index, choice in enumerate(choices, start=1):
            if not isinstance(choice, dict):
                return False, None, f'Choice {choice_index} in question {index} is invalid. Please try again.'

            choice_text = clean_text(choice.get('text'))
            is_correct = choice.get('is_correct')

            if not choice_text:
                return False, None, f'Choice {choice_index} in question {index} has no text. Please try again.'
            if not isinstance(is_correct, bool):
                return False, None, f'Choice {choice_index} in question {index} has an invalid correct flag. Please try again.'

            validated_choice = {
                'text': choice_text,
                'is_correct': is_correct,
            }
            validated_choices.append(validated_choice)
            if is_correct:
                correct_choices.append(validated_choice)

        if len(correct_choices) != 1:
            return False, None, f'Question {index} must have exactly 1 correct choice. Please try again.'
        if correct_answer != correct_choices[0]['text']:
            return False, None, f'Question {index} correct_answer must match the correct choice text. Please try again.'

        validated_questions.append({
            'text': text,
            'choices': validated_choices,
            'correct_answer': correct_answer,
            'explanation': explanation,
        })

    return True, {
        'title': title[:200],
        'questions': validated_questions,
    }, ''


def normalize_json_text(value):
    text = clean_text(value)
    if text.startswith('```json'):
        text = text[7:].strip()
    elif text.startswith('```'):
        text = text[3:].strip()
    if text.endswith('```'):
        text = text[:-3].strip()
    return text


def clean_text(value):
    if value is None:
        return ''
    return str(value).strip()
