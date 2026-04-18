import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

sentiment_model = None
sentiment_model_error = None
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"


def get_sentiment_model():
    global sentiment_model, sentiment_model_error

    if sentiment_model is None and sentiment_model_error is None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                local_files_only=not ALLOW_MODEL_DOWNLOADS
            )
            model = AutoModelForSequenceClassification.from_pretrained(
                MODEL_NAME,
                local_files_only=not ALLOW_MODEL_DOWNLOADS
            )
            sentiment_model = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                truncation=True,
                max_length=512
            )
        except Exception as exc:
            sentiment_model_error = exc

    if sentiment_model_error is not None:
        raise RuntimeError(
            "Sentiment model could not be loaded. Cache it locally or set ALLOW_MODEL_DOWNLOADS=1."
        ) from sentiment_model_error

    return sentiment_model

def analyze_sentiment(text):
    try:
        return get_sentiment_model()(text)
    except Exception as e:
        return [{"label": "ERROR", "score": 0.0, "message": str(e)}]
