from transformers import pipeline

sentiment_analyzer = pipeline('sentiment-analysis')

def analyze_sentiment(text):
    result = sentiment_analyzer(text[:512])[0]
    label = result['label']
    score = float(result['score'])
    if label == 'POSITIVE':
        return score, 'Positive'
    elif label == 'NEGATIVE':
        return -score, 'Negative'
    else:
        return 0.0, 'Neutral' 