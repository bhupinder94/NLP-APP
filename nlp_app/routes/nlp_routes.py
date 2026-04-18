#create api routes(production style) for nlp functionalities

from flask import Blueprint, request, jsonify
from nlp.keywords import extract_keywords
from nlp.ner import extract_entities
from nlp.sentiment import analyze_sentiment
from nlp.summarizer import summarize_long_text
from nlp.pipeline import analyze_text

nlp_bp = Blueprint('nlp', __name__)

@nlp_bp.route('/keywords', methods=['POST'])
def keywords_route():
    text = request.form.get('text')
    top_n = int(request.form.get('top_n', 10))

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        return jsonify(extract_keywords(text, top_n=top_n))
    except Exception as e:
        return jsonify({
            'error': 'Keyword extraction failed',
            'details': str(e)
        }), 500


@nlp_bp.route('/ner', methods=['POST'])
def ner_route():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        result = extract_entities(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': 'NER failed',
            'details': str(e)
        }), 500


@nlp_bp.route('/keywords-with-sentiment', methods=['POST'])
def keywords_with_sentiment_route():

    text = request.form.get('text')
    top_n = int(request.form.get('top_n', 10))

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    keywords = extract_keywords(text, top_n=top_n)
    sentiment = analyze_sentiment(text)

    return jsonify({'keywords': keywords, 'sentiment': sentiment})

@nlp_bp.route('/summarize', methods=['POST'])
def summarize_route():
    text = request.form.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:

      summary = summarize_long_text(text)
      return jsonify({'summary': summary})
    except Exception as e:
      return jsonify({
            'error': 'Summarization failed',
            'details' : str(e)
        }), 500
          
@nlp_bp.route('/sentiment', methods=['POST'])
def sentiment_route():
    text = request.form.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    result = analyze_sentiment(text)
    return jsonify(result)

@nlp_bp.route('/analyze', methods=['POST'])
def analyze_route():
    text = request.form.get('text')
    top_n = int(request.form.get('top_n', 10))

    if not text or not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    result = analyze_text(text, top_n_keywords=top_n)
    return jsonify(result)
