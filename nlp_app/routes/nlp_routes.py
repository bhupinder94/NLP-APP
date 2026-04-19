#create api routes(production style) for nlp functionalities

from flask import Blueprint, current_app, jsonify, request, session
from nlp.keywords import extract_keywords
from nlp.ner import extract_entities
from nlp.sentiment import analyze_sentiment
from nlp.summarizer import summarize_long_text
from nlp.pipeline import analyze_text

nlp_bp = Blueprint('nlp', __name__)


def save_history_if_logged_in(analysis_type, text, result):
    user_id = session.get('user_id')
    if not user_id:
        return

    db = current_app.config.get('db')
    if db is None:
        return

    db.save_analysis_history(user_id, analysis_type, text, result)

@nlp_bp.route('/keywords', methods=['POST'])
def keywords_route():
    text = request.form.get('text')
    top_n = int(request.form.get('top_n', 10))

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        result = extract_keywords(text, top_n=top_n)
        save_history_if_logged_in('keywords', text, result)
        return jsonify(result)
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
        save_history_if_logged_in('ner', text, result)
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

    try:
        keywords = extract_keywords(text, top_n=top_n)
        sentiment = analyze_sentiment(text)
        result = {'keywords': keywords, 'sentiment': sentiment}
        save_history_if_logged_in('keywords-with-sentiment', text, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'error': 'Keyword and sentiment analysis failed',
            'details': str(e)
        }), 500

@nlp_bp.route('/summarize', methods=['POST'])
def summarize_route():
    text = request.form.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:

      summary = summarize_long_text(text)
      result = {'summary': summary}
      save_history_if_logged_in('summary', text, result)
      return jsonify(result)
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
    save_history_if_logged_in('sentiment', text, result)
    return jsonify(result)

@nlp_bp.route('/analyze', methods=['POST'])
def analyze_route():
    text = request.form.get('text')
    top_n = int(request.form.get('top_n', 10))

    if not text or not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    result = analyze_text(text, top_n_keywords=top_n)
    save_history_if_logged_in('analyze', text, result)
    return jsonify(result)
