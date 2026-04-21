# Simple algorithm-based text classifier
# No AI model needed - instant classification!

# Word lists for emotion/category detection
EMOTION_WORDS = {
    'joy': ['happy', 'joy', 'love', 'wonderful', 'great', 'amazing', 'excellent', 'fantastic', 'delighted', 'pleased', 'grateful', 'blessed', 'excited', 'elated', 'cheerful', 'merry', 'laugh', 'smile', 'fun', 'enjoy', 'best', 'perfect', 'awesome', 'brilliant', 'glad', 'content'],
    'sadness': ['sad', 'unhappy', 'depressed', 'miserable', 'heartbroken', 'grief', 'sorrow', 'cry', 'tears', 'lonely', 'alone', 'lost', 'hopeless', 'devastated', 'gloomy', 'down', 'disappointed', 'hurt', 'pain', 'suffer', 'miss', 'regret', 'sorry', 'unfortunate'],
    'anger': ['angry', 'furious', 'mad', 'rage', 'hate', 'annoyed', 'irritated', 'frustrated', 'outraged', 'hostile', 'bitter', 'resentful', 'aggressive', 'violent', 'enraged', 'infuriated', 'livid', 'irate', 'mad', 'upset', 'offended'],
    'fear': ['afraid', 'scared', 'frightened', 'terrified', 'fear', 'anxious', 'worried', 'nervous', 'panic', 'horrified', 'dread', 'alarmed', 'concerned', 'uneasy', 'tense', 'apprehensive', 'coward', 'timid', 'shy', 'nervous'],
    'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'unexpected', 'stunned', 'startled', 'bewildered', 'astonished', 'incredible', 'unbelievable', 'wow', 'unusual', 'extraordinary', 'remarkable'],
    'disgust': ['disgusted', 'revolted', 'repelled', 'sick', 'nauseous', 'gross', 'terrible', 'awful', 'horrible', 'nasty', 'dislike', 'detest', 'loathe', 'despise', 'abhor'],
    'trust': ['trust', 'believe', 'faith', 'confident', 'reliable', 'honest', 'sincere', 'loyal', 'depend', 'certain', 'sure', 'hopeful', 'optimistic', 'positive', 'safe', 'secure'],
    'anticipation': ['expect', 'hope', 'look forward', 'waiting', 'soon', 'future', 'planning', 'prepare', 'eager', 'excited', 'waiting', 'predict', 'anticipate', 'await', 'soon']
}

CATEGORY_WORDS = {
    'technology': ['computer', 'software', 'hardware', 'internet', 'digital', 'ai', 'machine learning', 'data', 'algorithm', 'code', 'programming', 'developer', 'app', 'website', 'cloud', 'cyber', 'tech', 'robot', 'automation', 'smart'],
    'business': ['company', 'market', 'money', 'profit', 'sales', 'customer', 'business', 'trade', 'investment', 'stock', 'finance', 'economy', 'growth', 'revenue', 'industry', 'corporate', 'entrepreneur', 'startup', 'brand'],
    'health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'patient', 'treatment', 'medicine', 'symptom', 'healthcare', 'wellness', 'fitness', 'exercise', 'diet', 'nutrition', 'virus', 'infection', 'cancer', 'diabetes', 'heart'],
    'sports': ['game', 'player', 'team', 'match', 'win', 'score', 'goal', 'sport', 'football', 'cricket', 'basketball', 'tennis', 'championship', 'tournament', 'coach', 'athlete', 'run', 'play', 'ball'],
    'politics': ['government', 'president', 'minister', 'election', 'vote', 'political', 'party', 'congress', 'parliament', 'law', 'policy', 'democracy', 'leader', 'nation', 'country', 'citizen', 'rights', 'freedom'],
    'education': ['school', 'student', 'teacher', 'university', 'college', 'education', 'learn', 'study', 'course', 'exam', 'degree', 'class', 'lesson', 'book', 'knowledge', 'teach', 'academic', 'research', 'scholar'],
    'entertainment': ['movie', 'film', 'music', 'song', 'actor', 'actress', 'celebrity', 'star', 'Hollywood', 'Bollywood', 'Netflix', 'show', 'drama', 'comedy', 'entertainment', 'artist', 'concert', 'festival', 'dance'],
    'science': ['research', 'scientist', 'experiment', 'study', 'discovery', 'science', 'physics', 'chemistry', 'biology', 'space', 'universe', 'planet', 'climate', 'scientific', 'theory', 'laboratory', 'invention', 'innovate']
}

def classify_text(text):
    """
    Algorithm-based text classification.
    Returns emotion and category scores.
    Instant - no AI model needed!
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # Count emotion matches
    emotion_scores = {}
    for emotion, word_list in EMOTION_WORDS.items():
        score = 0
        for word in word_list:
            if word in text_lower:
                score += text_lower.count(word)
        if score > 0:
            emotion_scores[emotion] = score
    
    # Count category matches
    category_scores = {}
    for category, word_list in CATEGORY_WORDS.items():
        score = 0
        for word in word_list:
            if word in text_lower:
                score += text_lower.count(word)
        if score > 0:
            category_scores[category] = score
    
    results = []
    
    # Add top emotions
    if emotion_scores:
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        total = sum(e[1] for e in sorted_emotions)
        for emotion, score in sorted_emotions[:3]:
            results.append({
                'label': emotion.title(),
                'score': round(score / total, 2),
                'type': 'emotion'
            })
    
    # Add top categories
    if category_scores:
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        total = sum(c[1] for c in sorted_cats)
        for category, score in sorted_cats[:3]:
            results.append({
                'label': category.title(),
                'score': round(score / total, 2),
                'type': 'category'
            })
    
    if not results:
        results.append({'label': 'General', 'score': 1.0, 'type': 'category'})
    
    return results
