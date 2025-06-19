from bias_model import classify_bias
from sentiment_model import analyze_sentiment
from language_flags import detect_loaded_language

def analyze_text(text):
    bias_score, bias_label = classify_bias(text)
    sentiment_score, sentiment_label = analyze_sentiment(text)
    language_flags = detect_loaded_language(text)
    return {
        'bias_score': bias_score,
        'bias_label': bias_label,
        'sentiment_score': sentiment_score,
        'sentiment_label': sentiment_label,
        'language_flags': language_flags,
    } 