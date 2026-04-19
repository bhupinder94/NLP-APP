import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

classifier_model = None
classifier_model_error = None
MODEL_NAME = os.getenv("TEXT_CLASSIFIER_MODEL", "SamLowe/roberta-base-go_emotions")
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"
device_id = 0 if os.getenv("NLP_DEVICE", "cpu").strip().lower() == "cuda" and torch.cuda.is_available() else -1


def _is_cuda_error(exc):
    return "cuda" in str(exc).lower()


def _switch_to_cpu():
    global classifier_model, classifier_model_error, device_id
    if device_id == -1:
        return
    device_id = -1
    classifier_model = None
    classifier_model_error = None


def get_classifier_model():
    global classifier_model, classifier_model_error

    if classifier_model is None and classifier_model_error is None:
        try:
            classifier_model = pipeline(
                "text-classification",
                model=MODEL_NAME,
                device=device_id,
                top_k=None,
                truncation=True,
                max_length=512
            )
        except Exception as exc:
            classifier_model_error = exc

    if classifier_model_error is not None:
        raise RuntimeError(
            "Text classifier model could not be loaded. Cache it locally or set ALLOW_MODEL_DOWNLOADS=1."
        ) from classifier_model_error

    return classifier_model


def classify_text(text):
    try:
        return get_classifier_model()(text)
    except Exception as e:
        if _is_cuda_error(e):
            try:
                _switch_to_cpu()
                return get_classifier_model()(text)
            except Exception as retry_error:
                return [{"error": str(retry_error)}]
        return [{"error": str(e)}]