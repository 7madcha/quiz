import json


def build_groq_quiz_prompt(*, subject, domain, difficulty, number_of_questions):
    schema = {
        "title": "AI Quiz about subject",
        "questions": [
            {
                "text": "question text",
                "choices": [
                    {"text": "choice A", "is_correct": True},
                    {"text": "choice B", "is_correct": False},
                    {"text": "choice C", "is_correct": False},
                    {"text": "choice D", "is_correct": False},
                ],
                "correct_answer": "choice A",
                "explanation": "short explanation",
            }
        ],
    }

    return f"""
Create an educational quiz.

Subject: {subject}
Domain: {domain}
Difficulty: {difficulty}
Number of questions: {number_of_questions}

Return ONLY valid JSON matching this structure:
{json.dumps(schema, indent=2)}

Rules:
- Generate exactly {number_of_questions} questions.
- Each question must have exactly 4 choices.
- Exactly 1 choice per question must have is_correct=true.
- correct_answer must exactly match the correct choice text.
- Explanation must be short and pedagogical.
- Difficulty must match the selected difficulty.
- Domain and subject must be respected.
- No markdown.
- No code fences.
- No explanation outside JSON.
- JSON only.
""".strip()
