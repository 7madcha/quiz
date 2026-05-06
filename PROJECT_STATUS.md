# Project Status

This file summarizes what has been done on the Django quiz project so far.

## Current Setup

- Project name: `quizproject`
- Framework: Django
- Active pinned Django version: `Django==4.2.30`
- Database engine: MySQL through XAMPP
- Database name: `quiz_db`
- Database user: `root`
- Database password: empty
- Database host: `localhost`
- Database port: `3306`
- Charset: `utf8mb4`

The project originally had files generated with Django 6.0.4, but Django was downgraded to `4.2.30` because the local XAMPP MariaDB version is `10.4.32`. Newer Django versions require MariaDB 10.6 or later, which caused this error:

```text
django.db.utils.NotSupportedError: MariaDB 10.6 or later is required (found 10.4.32).
```

After the downgrade, the virtual environment `quizenv` was updated so it now uses Django `4.2.30`.

## Installed Apps

The project currently enables these local apps in `quizproject/settings.py`:

- `accounts`
- `quizzes`
- `attempts`
- `ai_generator`

The old `quiz` app still exists in the project folder, but it is currently commented out in `INSTALLED_APPS`.

## Database and Migrations

The project is configured to store its data in MySQL using XAMPP.

The database migrations have already been run successfully. The following migration groups are applied:

- `accounts`
- `admin`
- `attempts`
- `auth`
- `contenttypes`
- `quizzes`
- `sessions`

This means the database tables for users, admin, quizzes, teacher profiles, attempts, answers, sessions, and permissions already exist in MySQL.

## Main Models

### Accounts

`accounts.TeacherProfile`

- Links a Django `User` to a teacher profile.
- Stores the teacher domain.
- Tracks teacher validation status: `pending`, `approved`, or `rejected`.

### Quizzes

`quizzes.Domain`

- Stores quiz subject/domain categories.

`quizzes.Quiz`

- Stores quiz metadata such as title, subject, domain, difficulty, creator, AI-generated status, publication status, and creation date.

`quizzes.Question`

- Stores questions for a quiz.
- Supports multiple choice and true/false questions.
- Stores the correct answer, explanation, and point value.

`quizzes.Choice`

- Stores answer choices for quiz questions.
- Marks whether a choice is correct.

### Attempts

`attempts.QuizAttempt`

- Stores a user's attempt on a quiz.
- Tracks score, start date, submit date, and attempt status.

`attempts.Answer`

- Stores a user's answer for a question inside a quiz attempt.
- Tracks selected choice, text answer, correctness, and score.

## Commands Used

From the project folder:

```powershell
cd D:\codeC\testit\quizproject
```

Check the Django version used by the virtual environment:

```powershell
..\quizenv\Scripts\python.exe -m django --version
```

Install the pinned project dependencies:

```powershell
..\quizenv\Scripts\python.exe -m pip install -r requirements.txt
```

Check migration status:

```powershell
..\quizenv\Scripts\python.exe manage.py showmigrations
```

Create a superuser:

```powershell
..\quizenv\Scripts\python.exe manage.py createsuperuser
```

Run the development server:

```powershell
..\quizenv\Scripts\python.exe manage.py runserver
```

## Important Notes

- Start Apache/MySQL from XAMPP before running Django commands that need the database.
- Make sure the MySQL database `quiz_db` exists in phpMyAdmin.
- The current MariaDB version from XAMPP is compatible with Django `4.2.30`.
- Do not upgrade Django back to 6.x unless MariaDB is upgraded to 10.6 or later.
- The `DEFAULT_AUTO_FIELD` warnings are not blocking. They can be cleaned up later by adding a default primary key setting or app-level configuration.
