import spacy
import re

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Fallback if spacy model not available
    nlp = None

# Comprehensive list of loaded language terms
LOADED_TERMS = [
    # Emotional/Intense words
    'shocking', 'unprecedented', 'disaster', 'outrage', 'crisis', 'scandal', 
    'catastrophe', 'explosive', 'devastating', 'terrible', 'horrible', 'awful',
    'amazing', 'incredible', 'fantastic', 'brilliant', 'outstanding',
    
    # Political/Controversial terms
    'radical', 'extreme', 'dangerous', 'threatening', 'revolutionary',
    'corrupt', 'dishonest', 'heroic', 'brave', 'cowardly', 'treasonous',
    'unpatriotic', 'socialist', 'fascist', 'communist', 'dictator',
    
    # Exaggerated claims
    'everyone knows', 'clearly', 'obviously', 'undoubtedly', 'certainly',
    'absolutely', 'completely', 'totally', 'entirely', 'wholly',
    
    # Urgency/Scare tactics
    'urgent', 'immediate', 'critical', 'vital', 'essential', 'crucial',
    'time is running out', 'last chance', 'final warning', 'doomsday',
    
    # Partisan language
    'fake news', 'mainstream media', 'deep state', 'establishment',
    'elite', 'ordinary people', 'real americans', 'coastal elites'
]

def detect_loaded_language(text):
    """Detect loaded language in text"""
    if not text or len(text.strip()) < 10:
        return []
    
    flags = []
    text_lower = text.lower()
    
    # Simple pattern matching if spacy is not available
    if nlp is None:
        for term in LOADED_TERMS:
            if term in text_lower:
                # Find the context around the term
                start = text_lower.find(term)
                if start != -1:
                    # Get surrounding context
                    context_start = max(0, start - 50)
                    context_end = min(len(text), start + len(term) + 50)
                    snippet = text[context_start:context_end].strip()
                    flags.append({'snippet': snippet, 'term': term})
        return flags[:5]  # Limit to 5 flags
    
    # Use spacy for more sophisticated analysis
    try:
        doc = nlp(text)
        for i, token in enumerate(doc):
            if token.text.lower() in LOADED_TERMS:
                # Get context around the loaded term
                start_idx = max(0, i-2)
                end_idx = min(len(doc), i+3)
                snippet = ' '.join([t.text for t in doc[start_idx:end_idx]])
                flags.append({
                    'snippet': snippet, 
                    'term': token.text.lower(),
                    'index': token.idx
                })
    except Exception as e:
        print(f"Error in spacy analysis: {e}")
        # Fallback to simple matching
        for term in LOADED_TERMS:
            if term in text_lower:
                start = text_lower.find(term)
                if start != -1:
                    context_start = max(0, start - 50)
                    context_end = min(len(text), start + len(term) + 50)
                    snippet = text[context_start:context_end].strip()
                    flags.append({'snippet': snippet, 'term': term})
    
    # Remove duplicates and limit results
    unique_flags = []
    seen_snippets = set()
    for flag in flags:
        if flag['snippet'] not in seen_snippets:
            unique_flags.append(flag)
            seen_snippets.add(flag['snippet'])
    
    return unique_flags[:5]  # Return top 5 loaded language instances 