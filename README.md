# Quiz Project

A Django quiz project.

## Setup

Do not copy another developer's virtual environment folder. Each developer should
create their own environment locally and install the project dependencies from
`requirements.txt`.

```powershell
git clone https://github.com/7madcha/quiz.git
cd quiz
python -m venv quizenv
.\quizenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The project uses MySQL. Start MySQL with XAMPP or another local MySQL server,
then create a database named:

```text
quiz_db
```

After the database exists, run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```



## Groq API setup

Create a Groq API key, then set it in PowerShell before running the server:

```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
..\quizenv\Scripts\python.exe manage.py runserver


Open the site at:

```text
http://127.0.0.1:8000/
```

The virtual environment folder, local database data, and local machine settings
should not be committed to GitHub.

