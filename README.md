# TextChar AI

TextChar AI is a Flask-based NLP web application with user login/registration and an interactive dashboard for common text analysis tasks.

The app currently supports:

- Named Entity Recognition
- Sentiment Analysis
- Text Summarization
- Keyword Extraction
- Combined document analysis in a single workflow

## Features

- Flask web app with HTML templates for login, registration, and dashboard views
- NLP API routes under `/api`
- User authentication with hashed passwords using `bcrypt`
- MySQL support for user storage
- Automatic fallback to SQLite when MySQL is unavailable
- Lazy model loading so the app can start even when large NLP models are not preloaded

## Project Structure

```text
demosession_api13lecture/
├── README.md
├── .gitignore
├── .vscode/
├── myenv/
└── nlp_app/
    ├── app.py
    ├── db.py
    ├── requirements.txt
    ├── nlp/
    │   ├── keywords.py
    │   ├── ner.py
    │   ├── pipeline.py
    │   ├── sentiment.py
    │   └── summarizer.py
    ├── routes/
    │   └── nlp_routes.py
    └── templates/
        ├── login.html
        ├── register.html
        └── profile.html
```

## Tech Stack

- Python
- Flask
- Jinja2
- MySQL Connector
- SQLite
- bcrypt
- spaCy
- Transformers
- PyTorch
- KeyBERT
- Sentence Transformers

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/bhupinder94/NLP-APP.git
cd NLP-APP
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv myenv
.\myenv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv myenv
myenv\Scripts\activate
```

### 3. Install dependencies

Base dependencies from the project:

```bash
pip install -r nlp_app/requirements.txt
```

This app also imports NLP and database packages that should be installed in the same environment:

```bash
pip install requests bcrypt mysql-connector-python torch transformers sentence-transformers keybert spacy
```

Install the spaCy English model used for NER:

```bash
python -m spacy download en_core_web_md
```

## Environment Variables

The app reads database and app settings from environment variables.

Optional variables:

- `FLASK_SECRET_KEY`
- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `ALLOW_MODEL_DOWNLOADS`

Example in PowerShell:

```powershell
$env:FLASK_SECRET_KEY = "change-me"
$env:DB_HOST = "localhost"
$env:DB_USER = "root"
$env:DB_PASSWORD = "your-mysql-password"
$env:DB_NAME = "nlp_app"
$env:ALLOW_MODEL_DOWNLOADS = "1"
```

## Database Behavior

On startup, the app tries to connect to MySQL first.

- If MySQL is available and credentials are correct, user data is stored in MySQL.
- If MySQL is unavailable or authentication fails, the app falls back to SQLite.
- The SQLite fallback database is created at `nlp_app/nlp_app.db`.

This makes local development easier because the app can still run without a working MySQL server.

## Run the App

From the `nlp_app` directory:

```bash
cd nlp_app
python app.py
```

You should then see Flask running at:

```text
http://127.0.0.1:5000
```

Open that URL in your browser.

## Web Pages

- `/` -> Login page
- `/register` -> Registration page
- `/profile` -> Dashboard after login

## API Endpoints

All NLP routes are available under `/api`.

### `POST /api/keywords`

Extracts keywords from text.

Form fields:

- `text`
- `top_n` optional, default `10`

### `POST /api/ner`

Extracts named entities from text.

Form fields:

- `text`

### `POST /api/sentiment`

Runs sentiment analysis.

Form fields:

- `text`

### `POST /api/summarize`

Summarizes long text.

Form fields:

- `text`

### `POST /api/keywords-with-sentiment`

Returns both keywords and sentiment for the same text.

Form fields:

- `text`
- `top_n` optional, default `10`

### `POST /api/analyze`

Runs a combined pipeline for:

- summary
- sentiment
- keywords
- named entities

Form fields:

- `text`
- `top_n` optional, default `10`

## Notes on Models

- Sentiment, summarization, and keyword models load on first use.
- If models are not already cached locally, set `ALLOW_MODEL_DOWNLOADS=1` to allow downloading them.
- If internet access is blocked and models are not cached, those endpoints will return informative errors instead of crashing the app.
- NER requires the spaCy model `en_core_web_md` to be installed locally.

## Common Issues

### MySQL access denied

If you see a MySQL authentication error, either:

- set the correct `DB_PASSWORD`, or
- continue using the automatic SQLite fallback for local development

### App starts but browser does not open

Flask does not automatically open a browser window. Open:

```text
http://127.0.0.1:5000
```

manually.

### High system load in VS Code

If VS Code feels slow, avoid opening the large `myenv` folder as indexed workspace content. This repository already includes workspace settings to reduce that overhead.

## Future Improvements

- Add a complete `requirements.txt` for all NLP dependencies
- Add logout route and session cleanup
- Add better error handling in combined routes
- Add tests for API endpoints
- Add Docker support


