import os

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

# GPU if available (auto-detect)
device_id = 0 if torch.cuda.is_available() else -1

# Load summarization model
PRIMARY_MODEL_NAME = os.getenv("SUMMARIZER_MODEL", "t5-small")  
FALLBACK_MODEL_NAMES = ["t5-small", "sshleifer/distilbart-cnn-12-6"]
ALLOW_MODEL_DOWNLOADS = True

summarizer = None
tokenizer = None
summarizer_error = None
MAX_TOKENS = 512


def _summary_bounds(token_count):
    # Maximum bounds for longest summaries
    max_length = max(150, min(350, token_count // 2))
    min_length = max(80, min(150, max_length // 2))
    if min_length >= max_length:
        min_length = max(60, max_length - 40)
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
    # Add T5 prompt prefix
    prompt = "summarize: " + text
    try:
        return loaded_summarizer(
            prompt,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )[0]["summary_text"]
    except Exception as exc:
        if _is_cuda_error(exc):
            _switch_to_cpu()
            loaded_summarizer, _ = load_summarizer_resources()
            return loaded_summarizer(
                prompt,
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
         
#step 1: short summary (extractive)

def summarize_short(text):
    """
    Quick extractive summary - just first few sentences.
    Fast, no AI model needed.
    """
    text = text.strip()
    if len(text) < 100:
        return text
    
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    result = sentences[0].strip()
    if len(sentences) > 1 and len(sentences[1].strip()) > 10:
        result += ". " + sentences[1].strip()
    if len(sentences) > 2 and len(sentences[2].strip()) > 10:
        result += ". " + sentences[2].strip()
    return result


def summarize_fast(text):
    """
    Fast extractive summary for very long text (100k+ chars).
    Samples key sentences from throughout the text.
    No AI model - just algorithm.
    """
    text = text.strip()
    if len(text) < 100:
        return text
    
    # Split into sentences
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    if len(sentences) <= 3:
        return '. '.join(sentiments[:3])
    
    # Sample from beginning, middle, end
    n = len(sentences)
    selected = []
    
    # Always include first sentence
    selected.append(sentences[0])
    
    # Sample from middle and end
    if n > 5:
        selected.append(sentences[n // 2])
    if n > 10:
        selected.append(sentences[n * 2 // 3])
    
    # Last few sentences
    selected.append(sentences[-2])
    selected.append(sentences[-1])
    
    return '. '.join(s for s in selected if s) + '.'

#step 2: hierarchical summary

def summarize_long_text(text):

    """
    Smarter extractive - picks best sentences from throughout text.
    No AI model = instant for any length!
    """
    
    text = text.strip()
    if len(text) < 100:
        return text

    # Split into sentences
    sentences = text.replace('!', '.').replace('?', '.').replace(';', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    n = len(sentences)
    if n <= 3:
        return '. '.join(sentences)
    
    # Score sentences by position (first/last are important)
    scored = []
    for i, s in enumerate(sentences):
        score = 0
        # First sentences get higher score
        if i < n * 0.1:
            score += 3
        elif i < n * 0.2:
            score += 2
        # Last sentences important too
        elif i >= n * 0.8:
            score += 2
        elif i >= n * 0.6:
            score += 1
        # Longer sentences are better
        if len(s.split()) > 10:
            score += 1
        scored.append((score, i, s))  # Keep index for sorting
    
    # Sort by score and take top 6
    scored.sort(key=lambda x: x[0], reverse=True)
    topIndices = [s[1] for s in scored[:6]]
    topIndices.sort()  # Sort by original position
    
    final = [sentences[i] for i in topIndices if i < len(sentences)]
    return '. '.join(final) + '.'
 

    
    


