import spacy
nlp = spacy.load('en_core_web_sm')

LOADED_TERMS = [
    'shocking', 'unprecedented', 'disaster', 'outrage', 'crisis', 'scandal', 'catastrophe', 'explosive'
]

def detect_loaded_language(text):
    doc = nlp(text)
    flags = []
    for i, token in enumerate(doc):
        if token.text.lower() in LOADED_TERMS:
            snippet = ' '.join([t.text for t in doc[max(0, i-2):i+3]])
            flags.append({'snippet': snippet, 'index': token.idx})
    return flags 