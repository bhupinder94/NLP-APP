import os

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# Device selection

DEVICE = 0 if torch.cuda.is_available() else -1
 
# Load summerization model

MODEL_NAME = "facebook/bart-large-cnn"
ALLOW_MODEL_DOWNLOADS = os.getenv("ALLOW_MODEL_DOWNLOADS", "0") == "1"

summarizer = None
tokenizer = None
summarizer_error = None

MAX_TOKENS = 512

# UTITLITY: chunk text safely

def load_summarizer_resources():
    global summarizer, tokenizer, summarizer_error

    if (summarizer is None or tokenizer is None) and summarizer_error is None:
        try:
            loaded_tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                local_files_only=not ALLOW_MODEL_DOWNLOADS
            )
            loaded_model = AutoModelForSeq2SeqLM.from_pretrained(
                MODEL_NAME,
                local_files_only=not ALLOW_MODEL_DOWNLOADS
            )
            summarizer = pipeline(
                "summarization",
                model=loaded_model,
                tokenizer=loaded_tokenizer,
                device=DEVICE
            )
            tokenizer = loaded_tokenizer
        except Exception as exc:
            summarizer_error = exc

    if summarizer_error is not None:
        raise RuntimeError(
            "Summarization model could not be loaded. Cache it locally or set ALLOW_MODEL_DOWNLOADS=1."
        ) from summarizer_error

    return summarizer, tokenizer

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
            summary = loaded_summarizer(
                chunk,
                max_length = 150,
                min_length = 60,
                do_sample = False 
            )[0]["summary_text"]

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

    loaded_summarizer, _ = load_summarizer_resources()
    chunks = chunk_text(text)

    # Short text > summarize directly
    if len(chunks) == 1:
       return loaded_summarizer(
            text,
            max_length = 180,
            min_length = 80,
            do_sample = False
        )[0]["summary_text"]

    # Long text = hierarchical summarization
    chunk_summaries = summarize_chunks(chunks)

    combined_summary_text = " ".join(chunk_summaries)

    final_summary = loaded_summarizer(
        combined_summary_text,
        max_length = 200,
        min_length = 100,
        do_sample = False
    )[0]["summary_text"]
    return final_summary
 

    
    


