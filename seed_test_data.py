from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import TeacherProfile
from attempts.models import Answer, QuizAttempt
from quizzes.models import Choice, Domain, Question, Quiz


def ensure_user(username, password, *, email="", first_name="", last_name=""):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = True
    user.set_password(password)
    user.save()
    return user


def ensure_domain(name, description):
    domain, _ = Domain.objects.get_or_create(name=name)
    domain.description = description
    domain.save()
    return domain


def ensure_teacher(username, password, domain, *, first_name):
    user = ensure_user(
        username,
        password,
        email=f"{username}@test.local",
        first_name=first_name,
    )
    profile, _ = TeacherProfile.objects.get_or_create(user=user)
    profile.domain = domain
    profile.status = "approved"
    profile.save()
    return user


def ensure_quiz(*, title, subject, domain, difficulty, teacher, questions):
    quiz, _ = Quiz.objects.get_or_create(
        title=title,
        defaults={
            "subject": subject,
            "domain": domain,
            "difficulty": difficulty,
            "created_by": teacher,
            "status": "published",
        },
    )
    quiz.subject = subject
    quiz.domain = domain
    quiz.difficulty = difficulty
    quiz.created_by = teacher
    quiz.status = "published"
    quiz.is_ai_generated = False
    quiz.save()

    for item in questions:
        question, _ = Question.objects.get_or_create(
            quiz=quiz,
            text=item["text"],
            defaults={
                "question_type": "mcq",
                "correct_answer": item["correct"],
                "explanation": item["explanation"],
                "points": item.get("points", 1),
            },
        )
        question.question_type = "mcq"
        question.correct_answer = item["correct"]
        question.explanation = item["explanation"]
        question.points = item.get("points", 1)
        question.save()

        existing_choices = set(question.choices.values_list("text", flat=True))
        for choice_text in item["choices"]:
            if choice_text not in existing_choices:
                Choice.objects.create(
                    question=question,
                    text=choice_text,
                    is_correct=choice_text == item["correct"],
                )
            else:
                Choice.objects.filter(question=question, text=choice_text).update(
                    is_correct=choice_text == item["correct"]
                )
    return quiz


development = ensure_domain(
    "Development",
    "Programming, web development, software engineering, and application design.",
)
data = ensure_domain(
    "Data",
    "Databases, analytics, statistics, machine learning, and data handling.",
)

houssam = ensure_teacher("houssam", "rhdir2005", development, first_name="Houssam")
yassine = ensure_teacher("yassine", "abaki2005", data, first_name="Yassine")
youssef = ensure_user(
    "youssef",
    "zyadni2005",
    email="youssef@test.local",
    first_name="Youssef",
)

python_quiz = ensure_quiz(
    title="Python Basics Check",
    subject="Python",
    domain=development,
    difficulty="easy",
    teacher=houssam,
    questions=[
        {
            "text": "Which keyword defines a function in Python?",
            "correct": "def",
            "choices": ["def", "func", "function", "method"],
            "explanation": "Python uses the def keyword before the function name.",
        },
        {
            "text": "Which type stores key-value pairs?",
            "correct": "dict",
            "choices": ["list", "tuple", "dict", "set"],
            "explanation": "A dictionary stores values under keys.",
        },
        {
            "text": "What does len([1, 2, 3]) return?",
            "correct": "3",
            "choices": ["2", "3", "4", "None"],
            "explanation": "The list contains three items.",
        },
    ],
)

web_quiz = ensure_quiz(
    title="HTML and CSS Starter Quiz",
    subject="Web Development",
    domain=development,
    difficulty="medium",
    teacher=houssam,
    questions=[
        {
            "text": "Which HTML tag creates a link?",
            "correct": "a",
            "choices": ["a", "link", "href", "url"],
            "explanation": "The a element creates hyperlinks.",
        },
        {
            "text": "Which CSS property changes text color?",
            "correct": "color",
            "choices": ["font", "text-style", "color", "paint"],
            "explanation": "The color property controls text color.",
        },
    ],
)

data_quiz = ensure_quiz(
    title="Data Fundamentals",
    subject="Data",
    domain=data,
    difficulty="easy",
    teacher=yassine,
    questions=[
        {
            "text": "Which SQL command reads data from a table?",
            "correct": "SELECT",
            "choices": ["SELECT", "READ", "GET", "OPEN"],
            "explanation": "SELECT retrieves rows from database tables.",
        },
        {
            "text": "What is the average also called?",
            "correct": "Mean",
            "choices": ["Mode", "Median", "Mean", "Range"],
            "explanation": "The arithmetic average is called the mean.",
        },
        {
            "text": "Which file format commonly stores tabular data with commas?",
            "correct": "CSV",
            "choices": ["CSV", "PNG", "PDF", "MP3"],
            "explanation": "CSV means comma-separated values.",
        },
    ],
)

ai_pending_quiz = ensure_quiz(
    title="AI Generated SQL Practice",
    subject="SQL",
    domain=data,
    difficulty="medium",
    teacher=yassine,
    questions=[
        {
            "text": "Which clause filters rows in SQL?",
            "correct": "WHERE",
            "choices": ["WHERE", "ORDER", "GROUP", "TABLE"],
            "explanation": "WHERE applies row-level conditions.",
        },
        {
            "text": "Which SQL keyword sorts query results?",
            "correct": "ORDER BY",
            "choices": ["SORT", "ORDER BY", "ALIGN", "FILTER"],
            "explanation": "ORDER BY sorts the returned rows.",
        },
    ],
)
ai_pending_quiz.is_ai_generated = True
ai_pending_quiz.status = "pending"
ai_pending_quiz.save()

attempt, _ = QuizAttempt.objects.get_or_create(
    user=youssef,
    quiz=python_quiz,
    defaults={
        "status": "submitted",
        "score": 2,
        "submitted_at": timezone.now(),
    },
)
attempt.status = "submitted"
attempt.score = 2
attempt.submitted_at = timezone.now()
attempt.save()

answers = [
    ("Which keyword defines a function in Python?", "def"),
    ("Which type stores key-value pairs?", "list"),
    ("What does len([1, 2, 3]) return?", "3"),
]
for question_text, selected_text in answers:
    question = Question.objects.get(quiz=python_quiz, text=question_text)
    selected_choice = Choice.objects.get(question=question, text=selected_text)
    answer, _ = Answer.objects.get_or_create(attempt=attempt, question=question)
    answer.selected_choice = selected_choice
    answer.user_answer = selected_text
    answer.is_correct = selected_choice.is_correct
    answer.score = question.points if selected_choice.is_correct else 0
    answer.save()

print("Seed data ready.")
print("Domains: Development, Data")
print("Teachers: houssam, yassine")
print("Student: youssef")
print("Quizzes: Python Basics Check, HTML and CSS Starter Quiz, Data Fundamentals, AI Generated SQL Practice")
