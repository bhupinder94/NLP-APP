from nlp.summarizer import summarize_long_text
from nlp.sentiment import analyze_sentiment
from nlp.keywords import extract_keywords
from nlp.ner import extract_entities
from nlp.classifier import classify_text

def analyze_text(text, top_n_keywords=10):
    """
    central NLP pipeline.
    Runs multiple NLP tasks on the input text.

    """

    if not text or not text.strip():
        return {"error": "No text provided"}
    
    result = {}

    # 1. Summarization (long-text-safe)
    try:
        result['summary'] = summarize_long_text(text)
    except Exception as e:
        result["summary"] = None
        result["summary_error"] = str(e)

    # 2. Sentiment analysis
    
    # try:
    #     sentiment = analyze_sentiment(text)
    #     if isinstance(sentiment, list) and len(sentiment) > 0:
    #         result["sentiment"] = sentiment[0]  # always object
    #     else:
    #         result["sentiment"] = {"label": "UNKNOWN", "score": 0.0}
    # except Exception as e:
    #     result["sentiment"] = {"label": "ERROR", "score": 0.0}
    #     result["sentiment_error"] = str(e)
    
    # 2. Sentiment analysis (ALWAYS return a dict)
    try:
        sentiment = analyze_sentiment(text)

        if isinstance(sentiment, list) and len(sentiment) > 0:
          result["sentiment"] = {
            "label": sentiment[0]["label"],
            "score": float(sentiment[0]["score"])
        }
        else:
          result["sentiment"] = {
            "label": "UNKNOWN",
            "score": 0.0
          }

    except Exception as e:
       result["sentiment"] = {
        "label": "ERROR",
        "score": 0.0
       }
       result["sentiment_error"] = str(e)



    # 3. Keyword extraction
    try:
        result ["keywords"] = extract_keywords(text, top_n=top_n_keywords)
    except Exception as e:
        result["keywords"] = []
        result["keywords_error"] = str(e)

    # 4. Named Entity Recognition
    try:
        result["entities"] = extract_entities(text)
    except Exception as e:
        result["entities"] = []
        result["entities_error"] = str(e)

    # 5. Text Classification (algorithm-based)
    try:
        result["classification"] = classify_text(text)
    except Exception as e:
        result["classification"] = []
        result["classification_error"] = str(e)

    return result        

    




    
