import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

sentiment_model = None
sentiment_model_error = None
MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
ALLOW_MODEL_DOWNLOADS = True
device_id = 0 if torch.cuda.is_available() else -1


def _is_cuda_error(exc):
    return "cuda" in str(exc).lower()


def _switch_to_cpu():
    global sentiment_model, sentiment_model_error, device_id
    if device_id == -1:
        return
    device_id = -1
    sentiment_model = None
    sentiment_model_error = None


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
                device=device_id,
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

MAX_TEXT_LENGTH = 1500

def analyze_sentiment(text):
    # Truncate long text for model compatibility
    truncated = text.strip()[:MAX_TEXT_LENGTH]
    try:
        return get_sentiment_model()(truncated)
    except Exception as e:
        if _is_cuda_error(e):
            try:
                _switch_to_cpu()
                return get_sentiment_model()(truncated)
            except Exception as retry_error:
                return [{"label": "ERROR", "score": 0.0, "message": str(retry_error)}]
        return [{"label": "ERROR", "score": 0.0, "message": str(e)}]
