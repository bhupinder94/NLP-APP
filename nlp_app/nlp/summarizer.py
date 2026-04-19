import os

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Device selection

def _requested_device():
    requested = os.getenv("NLP_DEVICE", "cpu").strip().lower()
    if requested == "cuda" and torch.cuda.is_available():
        return 0
    return -1


def _is_cuda_error(exc):
    return "cuda" in str(exc).lower()
 
# Load summarization model

PRIMARY_MODEL_NAME = os.getenv("SUMMARIZER_MODEL", "google/pegasus-xsum")
FALLBACK_MODEL_NAMES = [PRIMARY_MODEL_NAME, "sshleifer/distilbart-cnn-12-6", "facebook/bart-large-cnn"]
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"

summarizer = None
tokenizer = None
summarizer_error = None
device_id = _requested_device()

MAX_TOKENS = 512  # Larger chunks = fewer chunks = faster


def _summary_bounds(token_count):
    # Much larger bounds for longer, more informative summaries
    max_length = max(100, min(280, token_count // 2))
    min_length = max(50, min(120, max_length // 2))
    if min_length >= max_length:
        min_length = max(40, max_length - 30)
    return min_length, max_length

# UTITLITY: chunk text safely

def load_summarizer_resources():
    global summarizer, tokenizer, summarizer_error

    if (summarizer is None or tokenizer is None) and summarizer_error is None:
        last_error = None
        for model_name in dict.fromkeys(FALLBACK_MODEL_NAMES):
            try:
                loaded_tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    local_files_only=not ALLOW_MODEL_DOWNLOADS
                )
                loaded_model = AutoModelForSeq2SeqLM.from_pretrained(
                    model_name,
                    local_files_only=not ALLOW_MODEL_DOWNLOADS
                )
                summarizer = pipeline(
                    "summarization",
                    model=loaded_model,
                    tokenizer=loaded_tokenizer,
                    device=device_id
                )
                tokenizer = loaded_tokenizer
                break
            except Exception as exc:
                last_error = exc

        if summarizer is None or tokenizer is None:
            summarizer_error = last_error

    if summarizer_error is not None:
        raise RuntimeError(
            "Summarization model could not be loaded. Cache it locally or set ALLOW_MODEL_DOWNLOADS=1."
        ) from summarizer_error

    return summarizer, tokenizer


def _switch_to_cpu():
    global summarizer, tokenizer, summarizer_error, device_id
    if device_id == -1:
        return
    device_id = -1
    summarizer = None
    tokenizer = None
    summarizer_error = None


def _run_summary(text, min_length, max_length):
    loaded_summarizer, _ = load_summarizer_resources()
    try:
        return loaded_summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )[0]["summary_text"]
    except Exception as exc:
        if _is_cuda_error(exc):
            _switch_to_cpu()
            loaded_summarizer, _ = load_summarizer_resources()
            return loaded_summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]["summary_text"]
        raise

def chunk_text(text, max_tokens=MAX_TOKENS):
    _, loaded_tokenizer = load_summarizer_resources()
    tokens = loaded_tokenizer.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = loaded_tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)

    return chunks
    
# step 1: summarize each chunks

def summarize_chunks(chunks):
    loaded_summarizer, _ = load_summarizer_resources()
    summaries = []

    for chunk in chunks:
        try:
            chunk_token_count = len(chunk.split())
            min_length, max_length = _summary_bounds(chunk_token_count)
            summary = _run_summary(chunk, min_length, max_length)
            summaries.append(summary)

        except Exception as e:
            summaries.append(chunk[:500])    #fallback safety

    return summaries
         
#step 2: hierarchical summary

def summarize_long_text(text):

    """
    Handles ANY length input safely.
    Returns a single coherent summary.
    """

    chunks = chunk_text(text)
    token_count = len(text.split())

    # Direct summarization - skip hierarchical for speed
    if len(chunks) == 1:
       if token_count < 40:
           return text.strip()

       min_length, max_length = _summary_bounds(token_count)
       return _run_summary(text, min_length, max_length)

    # Simple concatenation for multi-chunk - just combine all summaries
    chunk_summaries = summarize_chunks(chunks)
    return " ".join(chunk_summaries)
 

    
    


