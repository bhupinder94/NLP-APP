# TextChar AI

TextChar AI is a Flask-based NLP web application with user login/registration and an interactive dashboard for text analysis tasks.

## Features

### NLP Tools
- **Text Summarization** - 3 options: Quick Summary, Key Points, Smart Summary
- **Sentiment Analysis** - Detect positive/negative tone
- **Keyword Extraction** - Find key phrases
- **Text Classifier** - Detect emotions/categories (algorithm-based)
- **Named Entity Recognition** - Extract names, places, organizations
- **AI Workspace** - Complete analysis in one click

### Additional Features
- **URL Extraction** - Load articles from any URL (uses Playwright browser automation)
- **GPU Support** - Automatic GPU detection for faster AI processing
- **Live Character Count** - Shows character/word count as you type
- **Analysis History** - Save and review past analyses

## Tech Stack

- Python, Flask, Jinja2
- MySQL/SQLite, bcrypt
- PyTorch, Transformers, spaCy
- KeyBERT, Sentence Transformers
- Playwright (URL extraction)
- GPU acceleration

## Setup

```bash
# Clone
git clone https://github.com/bhupinder94/NLP-APP.git
cd NLP-APP

# Create virtual environment
python -m venv myenv
myenv\Scripts\activate

# Install dependencies
pip install -r nlp_app/requirements.txt

# Install spaCy model
python -m spacy download en_core_web_md

# Run
cd nlp_app
python app.py
```

## Environment Variables

Optional (PowerShell):
```powershell
$env:FLASK_SECRET_KEY = "change-me"
$env:NLP_DEVICE = "cuda"  # Use GPU if available
```

## Running the App

```bash
cd nlp_app
python app.py
```

Then open: http://127.0.0.1:5000

## Tab Order

Side navigation: Summary → Sentiment → Keywords → Classifier → NER → AI Workspace → History

## API Endpoints

All NLP routes under `/api`:

| Endpoint | Description |
|----------|-------------|
| `/api/summarize` | Summarize text (params: text, length=short/long/fast) |
| `/api/sentiment` | Sentiment analysis |
| `/api/keywords` | Extract keywords |
| `/api/ner` | Named entity recognition |
| `/api/classify` | Text classification |
| `/api/analyze` | Full pipeline analysis |
| `/api/extract-url` | Extract text from URL |

## Summary Options

| Option | Speed | Method |
|--------|-------|--------|
| Quick Summary | Instant | Extracts key sentences |
| Key Points | Instant | First 3 sentences |
| Smart Summary | Instant | Scored extractive |
| Full AI | Uses AI model | Neural summarization |

## GPU Support

The app automatically detects GPU if available. For faster AI:

```cmd
set NLP_DEVICE=cuda
python app.py
```

## Notes on Models

- AI models load on first use
- Set `ALLOW_MODEL_DOWNLOADS=1` to auto-download models
- GPU makes AI processing 10-50x faster

## License

MIT License