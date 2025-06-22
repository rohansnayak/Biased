from transformers import pipeline
import random

sentiment_analyzer = pipeline('sentiment-analysis')

def analyze_sentiment(text):
    if not text or len(text.strip()) < 10:
        return 0.0, 'Neutral'
    
    try:
        result = sentiment_analyzer(text[:512])[0]
        label = result['label']
        score = float(result['score'])
        
        # Map sentiment scores to more realistic ranges
        if label == 'POSITIVE':
            # Positive sentiment: 0.1 to 0.9
            sentiment_score = 0.1 + (score * 0.8)
            sentiment_label = 'Positive'
        elif label == 'NEGATIVE':
            # Negative sentiment: -0.9 to -0.1
            sentiment_score = -0.9 + (score * 0.8)
            sentiment_label = 'Negative'
        else:
            # Neutral sentiment: -0.1 to 0.1
            sentiment_score = random.uniform(-0.1, 0.1)
            sentiment_label = 'Neutral'
        
        # Add some variation based on text content
        text_lower = text.lower()
        
        # Check for emotional words that might affect sentiment
        positive_words = ['great', 'amazing', 'wonderful', 'excellent', 'fantastic', 'brilliant']
        negative_words = ['terrible', 'awful', 'horrible', 'disastrous', 'catastrophic', 'devastating']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment_score += 0.1
        elif neg_count > pos_count:
            sentiment_score -= 0.1
        
        # Clamp score to valid range
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        return sentiment_score, sentiment_label
        
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        # Fallback to neutral
        return 0.0, 'Neutral' 