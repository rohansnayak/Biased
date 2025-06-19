from transformers import pipeline
import numpy as np

try:
    bias_classifier = pipeline('text-classification', model='mrm8488/bert-tiny-finetuned-fake-news-detection')
except Exception:
    bias_classifier = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')

LABEL_MAP = {
    'FAKE': ('Right', 0.8),
    'REAL': ('Left', 0.2),
    'POSITIVE': ('Center', 0.3),
    'NEGATIVE': ('Right', 0.7),
}

def classify_bias(text):
    result = bias_classifier(text[:512])[0]
    label = result['label']
    score = float(result['score'])
    mapped_label, mapped_score = LABEL_MAP.get(label, ('Center', 0.5))
    return mapped_score, mapped_label 