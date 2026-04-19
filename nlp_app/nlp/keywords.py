import os

import torch
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

kw_model = None
kw_model_error = None
MODEL_NAME = "all-MiniLM-L6-v2"
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"
model_device = "cuda" if os.getenv("NLP_DEVICE", "cpu").strip().lower() == "cuda" and torch.cuda.is_available() else "cpu"
MAX_KEYWORD_TEXT_LENGTH = 2500


def _is_cuda_error(exc):
    return "cuda" in str(exc).lower()


def _switch_to_cpu():
    global kw_model, kw_model_error, model_device
    if model_device == "cpu":
        return
    model_device = "cpu"
    kw_model = None
    kw_model_error = None


def get_keyword_model():
    global kw_model, kw_model_error

    if kw_model is None and kw_model_error is None:
        try:
            embedding_model = SentenceTransformer(
                MODEL_NAME,
                device=model_device,
                local_files_only=not ALLOW_MODEL_DOWNLOADS
            )
            kw_model = KeyBERT(model=embedding_model)
        except Exception as exc:
            kw_model_error = exc

    if kw_model_error is not None:
        raise RuntimeError(
            "Keyword model could not be loaded. Cache the sentence-transformer model locally or set ALLOW_MODEL_DOWNLOADS=1."
        ) from kw_model_error

    return kw_model

MAX_KEYWORD_TEXT_LENGTH = 2500

def extract_keywords(text, top_n=10):
    truncated = text.strip()[:MAX_KEYWORD_TEXT_LENGTH]
    try:
        return get_keyword_model().extract_keywords(
            truncated,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=top_n
        )
    except Exception as exc:
        if _is_cuda_error(exc):
            _switch_to_cpu()
            return get_keyword_model().extract_keywords(
                truncated,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n
            )
        raise
