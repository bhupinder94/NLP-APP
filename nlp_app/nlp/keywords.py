import os

from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

kw_model = None
kw_model_error = None
MODEL_NAME = "all-MiniLM-L6-v2"
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"


def get_keyword_model():
    global kw_model, kw_model_error

    if kw_model is None and kw_model_error is None:
        try:
            embedding_model = SentenceTransformer(
                MODEL_NAME,
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

def extract_keywords(text, top_n=10):
    keywords = get_keyword_model().extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        top_n = top_n
    )

    return keywords
