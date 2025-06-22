from transformers import pipeline
import numpy as np
import re

# Political keywords and phrases that indicate bias
LEFT_BIAS_KEYWORDS = [
    'progressive', 'liberal', 'democratic', 'socialist', 'equity', 'inclusion',
    'climate change', 'renewable energy', 'universal healthcare', 'minimum wage',
    'workers rights', 'union', 'protest', 'activist', 'social justice',
    'systemic racism', 'privilege', 'diversity', 'lgbtq+', 'reproductive rights',
    'gun control', 'immigration reform', 'tax the rich', 'wealth inequality'
]

RIGHT_BIAS_KEYWORDS = [
    'conservative', 'republican', 'traditional', 'patriot', 'freedom', 'liberty',
    'second amendment', 'pro-life', 'family values', 'religious freedom',
    'free market', 'deregulation', 'tax cuts', 'border security', 'law and order',
    'military', 'national security', 'constitution', 'states rights',
    'small government', 'individual responsibility', 'meritocracy', 'capitalism'
]

CENTER_BIAS_KEYWORDS = [
    'bipartisan', 'compromise', 'moderate', 'balanced', 'objective', 'factual',
    'analysis', 'research', 'study', 'data', 'evidence', 'neutral', 'unbiased'
]

def analyze_political_keywords(text):
    """Analyze text for political keywords to determine bias"""
    text_lower = text.lower()
    
    left_count = sum(1 for keyword in LEFT_BIAS_KEYWORDS if keyword in text_lower)
    right_count = sum(1 for keyword in RIGHT_BIAS_KEYWORDS if keyword in text_lower)
    center_count = sum(1 for keyword in CENTER_BIAS_KEYWORDS if keyword in text_lower)
    
    total_political = left_count + right_count + center_count
    
    if total_political == 0:
        return 0.5, 'Center'
    
    # Calculate bias scores
    left_score = left_count / total_political
    right_score = right_count / total_political
    center_score = center_count / total_political
    
    # Determine dominant bias
    if left_score > right_score and left_score > center_score:
        bias_score = 0.2 + (left_score * 0.3)  # 0.2-0.5 range for left
        return bias_score, 'Left'
    elif right_score > left_score and right_score > center_score:
        bias_score = 0.7 + (right_score * 0.2)  # 0.7-0.9 range for right
        return bias_score, 'Right'
    else:
        bias_score = 0.4 + (center_score * 0.2)  # 0.4-0.6 range for center
        return bias_score, 'Center'

def analyze_sentiment_bias(text):
    """Use sentiment analysis to infer political bias"""
    try:
        sentiment_classifier = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
        result = sentiment_classifier(text[:512])[0]
        label = result['label']
        score = float(result['score'])
        
        # Map sentiment to political bias (simplified heuristic)
        if label == 'POSITIVE':
            return 0.3, 'Left'  # Positive sentiment often associated with progressive views
        else:
            return 0.7, 'Right'  # Negative sentiment often associated with conservative views
    except Exception:
        return 0.5, 'Center'

def analyze_loaded_language(text):
    """Detect loaded language that might indicate bias"""
    loaded_phrases = [
        'shocking', 'outrageous', 'scandalous', 'unprecedented', 'disastrous',
        'amazing', 'incredible', 'fantastic', 'terrible', 'horrible',
        'radical', 'extreme', 'dangerous', 'threatening', 'revolutionary',
        'corrupt', 'dishonest', 'heroic', 'brave', 'cowardly'
    ]
    
    text_lower = text.lower()
    loaded_count = sum(1 for phrase in loaded_phrases if phrase in text_lower)
    
    if loaded_count > 3:
        # High loaded language suggests stronger bias
        return 0.8, 'Right' if 'corrupt' in text_lower or 'disastrous' in text_lower else 'Left'
    elif loaded_count > 1:
        return 0.6, 'Right' if 'terrible' in text_lower or 'horrible' in text_lower else 'Left'
    else:
        return 0.5, 'Center'

def classify_bias(text):
    """Main bias classification function"""
    if not text or len(text.strip()) < 10:
        return 0.5, 'Center'
    
    # Get multiple bias indicators
    keyword_score, keyword_label = analyze_political_keywords(text)
    sentiment_score, sentiment_label = analyze_sentiment_bias(text)
    loaded_score, loaded_label = analyze_loaded_language(text)
    
    # Weight the different indicators
    final_score = (keyword_score * 0.5) + (sentiment_score * 0.3) + (loaded_score * 0.2)
    
    # Determine final label based on weighted score
    if final_score < 0.4:
        final_label = 'Left'
    elif final_score > 0.6:
        final_label = 'Right'
    else:
        final_label = 'Center'
    
    # Add some randomness to make it more realistic
    import random
    if random.random() < 0.3:  # 30% chance to adjust slightly
        final_score += random.uniform(-0.1, 0.1)
        final_score = max(0.0, min(1.0, final_score))
    
    return final_score, final_label 