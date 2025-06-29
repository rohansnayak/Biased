from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import re
import json
import os
from typing import Dict, List, Tuple, Optional

# Enhanced political keywords and phrases with context
LEFT_BIAS_PATTERNS = {
    'economic': [
        'wealth inequality', 'income gap', 'minimum wage increase', 'universal basic income',
        'progressive taxation', 'tax the rich', 'corporate greed', 'workers rights',
        'union organizing', 'labor rights', 'living wage', 'economic justice',
        'wealth redistribution', 'social safety net', 'affordable housing',
        'progressive', 'liberal', 'democratic', 'socialist', 'equity', 'inclusion',
        'workers deserve', 'corporate accountability', 'economic reform', 'fair wages'
    ],
    'social': [
        'systemic racism', 'white privilege', 'racial justice', 'police reform',
        'defund the police', 'black lives matter', 'lgbtq+ rights', 'transgender rights',
        'reproductive rights', 'abortion access', 'gender equality', 'feminism',
        'immigration reform', 'dreamers', 'path to citizenship', 'diversity inclusion',
        'social justice', 'civil rights', 'equality', 'inclusion', 'diversity',
        'police brutality', 'racial inequality', 'gender pay gap', 'women rights'
    ],
    'environmental': [
        'climate change', 'global warming', 'renewable energy', 'fossil fuels',
        'green new deal', 'carbon tax', 'environmental justice', 'sustainability',
        'clean energy', 'carbon emissions', 'climate action', 'environmental protection',
        'climate crisis', 'environmental destruction', 'pollution', 'green energy',
        'solar power', 'wind energy', 'carbon footprint', 'environmental impact'
    ],
    'healthcare': [
        'universal healthcare', 'medicare for all', 'single payer', 'healthcare is a right',
        'affordable care act', 'obamacare', 'healthcare reform', 'prescription drug prices',
        'healthcare access', 'medical care', 'health insurance', 'public health'
    ]
}

RIGHT_BIAS_PATTERNS = {
    'economic': [
        'free market', 'deregulation', 'tax cuts', 'small government', 'fiscal responsibility',
        'balanced budget', 'deficit reduction', 'supply side economics', 'trickle down',
        'corporate tax cuts', 'business friendly', 'job creators', 'economic freedom',
        'private sector', 'market solutions', 'government waste', 'conservative',
        'republican', 'traditional', 'patriot', 'freedom', 'liberty', 'capitalism',
        'free enterprise', 'economic growth', 'business growth', 'entrepreneurship'
    ],
    'social': [
        'traditional values', 'family values', 'religious freedom', 'pro life',
        'second amendment', 'gun rights', 'law and order', 'tough on crime',
        'border security', 'illegal immigration', 'america first', 'patriotism',
        'constitutional rights', 'states rights', 'individual responsibility',
        'family', 'religion', 'faith', 'morality', 'values', 'tradition',
        'gun control', 'second amendment rights', 'law enforcement', 'police support'
    ],
    'environmental': [
        'energy independence', 'drill baby drill', 'fracking', 'coal industry',
        'climate skepticism', 'global warming hoax', 'environmental overreach',
        'regulatory burden', 'energy dominance', 'american energy', 'fossil fuels',
        'oil industry', 'natural gas', 'energy production', 'domestic energy'
    ],
    'foreign_policy': [
        'military strength', 'national security', 'defense spending', 'american leadership',
        'tough on china', 'trade wars', 'protectionism', 'isolationism',
        'military', 'defense', 'national defense', 'security', 'foreign policy'
    ]
}

CENTER_BIAS_PATTERNS = [
    'bipartisan', 'compromise', 'moderate', 'balanced', 'objective', 'factual',
    'analysis', 'research', 'study', 'data', 'evidence', 'neutral', 'unbiased',
    'both sides', 'middle ground', 'pragmatic', 'centrist', 'nonpartisan',
    'independent', 'factual', 'evidence-based', 'data-driven', 'research shows'
]

# Loaded language patterns that indicate bias
LOADED_LANGUAGE = {
    'emotional': [
        'shocking', 'outrageous', 'scandalous', 'unprecedented', 'disastrous',
        'amazing', 'incredible', 'fantastic', 'terrible', 'horrible',
        'radical', 'extreme', 'dangerous', 'threatening', 'revolutionary',
        'crisis', 'emergency', 'urgent', 'critical', 'vital', 'essential'
    ],
    'judgmental': [
        'corrupt', 'dishonest', 'heroic', 'brave', 'cowardly', 'greedy',
        'selfish', 'noble', 'virtuous', 'evil', 'good', 'bad', 'wrong',
        'right', 'moral', 'immoral', 'ethical', 'unethical', 'responsible',
        'irresponsible', 'accountable', 'unaccountable'
    ],
    'partisan': [
        'radical left', 'far right', 'socialist agenda', 'conservative agenda',
        'liberal media', 'fake news', 'deep state', 'establishment',
        'left-wing', 'right-wing', 'liberal elite', 'conservative base',
        'progressive agenda', 'republican agenda', 'democratic agenda'
    ]
}

# Research-backed keywords (extra weight)
LEFT_RESEARCH = [
    'inequality', 'marginalized', 'systemic', 'equity', 'climate', 'justice', 'diversity',
    'reform', 'progressive', 'corporate', 'labor', 'activism', 'discrimination',
    'intersectionality', 'welfare'
]
CENTER_RESEARCH = [
    'policy', 'debate', 'committee', 'bipartisan', 'analysis', 'regulation', 'budget',
    'oversight', 'moderate', 'proposal', 'outcome', 'stakeholder', 'amendment', 'hearing', 'consensus'
]
RIGHT_RESEARCH = [
    'liberty', 'freedom', 'security', 'border', 'constitutional', 'conservative', 'deregulation',
    'taxpayer', 'sovereignty', 'traditional', 'defend', 'mandate', 'entrepreneur', 'family', 'authority'
]

# Add research-backed terms to patterns (with extra weight in scoring)
for word in LEFT_RESEARCH:
    for cat in LEFT_BIAS_PATTERNS:
        if word not in LEFT_BIAS_PATTERNS[cat]:
            LEFT_BIAS_PATTERNS[cat].append(word)
for word in RIGHT_RESEARCH:
    for cat in RIGHT_BIAS_PATTERNS:
        if word not in RIGHT_BIAS_PATTERNS[cat]:
            RIGHT_BIAS_PATTERNS[cat].append(word)
for word in CENTER_RESEARCH:
    if word not in CENTER_BIAS_PATTERNS:
        CENTER_BIAS_PATTERNS.append(word)

class PoliticalBiasAnalyzer:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.sentiment_classifier = None
        
        # Initialize sentiment classifier
        try:
            self.sentiment_classifier = pipeline('sentiment-analysis', 
                                               model='distilbert-base-uncased-finetuned-sst-2-english')
        except Exception as e:
            print(f"Warning: Could not load sentiment classifier: {e}")
    
    def analyze_political_keywords(self, text: str) -> Tuple[float, str, Dict]:
        """Analyze text for political keywords with context and weighting"""
        text_lower = text.lower()
        
        # Count keywords by category
        left_scores = {}
        right_scores = {}
        center_count = 0
        
        # Analyze left bias patterns
        for category, patterns in LEFT_BIAS_PATTERNS.items():
            count = 0
            for pattern in patterns:
                if pattern in text_lower:
                    # Give extra weight to research-backed terms
                    if pattern in LEFT_RESEARCH:
                        count += 2  # double weight
                    else:
                        count += 1
            if count > 0:
                left_scores[category] = count
        
        # Analyze right bias patterns
        for category, patterns in RIGHT_BIAS_PATTERNS.items():
            count = 0
            for pattern in patterns:
                if pattern in text_lower:
                    if pattern in RIGHT_RESEARCH:
                        count += 2
                    else:
                        count += 1
            if count > 0:
                right_scores[category] = count
        
        # Count center patterns
        for pattern in CENTER_BIAS_PATTERNS:
            if pattern in text_lower:
                if pattern in CENTER_RESEARCH:
                    center_count += 2
                else:
                    center_count += 1
        
        # Calculate weighted scores
        left_total = sum(left_scores.values())
        right_total = sum(right_scores.values())
        total_political = left_total + right_total + center_count
        
        if total_political == 0:
            return 0.5, 'Center', {'left': 0, 'right': 0, 'center': 0}
        
        # Weight categories differently - make left bias more sensitive
        left_weighted = (
            left_scores.get('economic', 0) * 1.5 +  # Increased weight
            left_scores.get('social', 0) * 1.3 +    # Increased weight
            left_scores.get('environmental', 0) * 1.2 +  # Increased weight
            left_scores.get('healthcare', 0) * 1.4   # Increased weight
        )
        
        right_weighted = (
            right_scores.get('economic', 0) * 1.3 +
            right_scores.get('social', 0) * 1.2 +
            right_scores.get('environmental', 0) * 1.0 +
            right_scores.get('foreign_policy', 0) * 1.1
        )
        
        # Calculate bias scores
        left_score = left_weighted / total_political
        right_score = right_weighted / total_political
        center_score = center_count / total_political
        
        # More sensitive thresholds for left bias detection
        if left_score > 0.1:  # Lower threshold for left bias
            bias_score = 0.15 + (left_score * 0.35)  # 0.15-0.5 range for left
            return bias_score, 'Left', {'left': left_score, 'right': right_score, 'center': center_score}
        elif right_score > 0.1:  # Lower threshold for right bias
            bias_score = 0.65 + (right_score * 0.25)  # 0.65-0.9 range for right
            return bias_score, 'Right', {'left': left_score, 'right': right_score, 'center': center_score}
        else:
            bias_score = 0.4 + (center_score * 0.2)  # 0.4-0.6 range for center
            return bias_score, 'Center', {'left': left_score, 'right': right_score, 'center': center_score}
    
    def analyze_sentiment_context(self, text: str) -> Tuple[float, str]:
        """Analyze sentiment with political context"""
        if not self.sentiment_classifier:
            return 0.5, 'Center'
        
        try:
            # Split text into chunks for better analysis
            chunks = self._split_text_into_chunks(text, 512)
            sentiment_scores = []
            
            for chunk in chunks[:3]:  # Analyze first 3 chunks
                if len(chunk.strip()) < 10:
                    continue
                    
                result = self.sentiment_classifier(chunk)[0]
                label = result['label']
                score = float(result['score'])
                
                # More nuanced sentiment to political bias mapping
                if label == 'POSITIVE':
                    # Check if positive sentiment is about progressive issues
                    if any(pattern in chunk.lower() for pattern in LEFT_BIAS_PATTERNS['social'] + LEFT_BIAS_PATTERNS['environmental']):
                        sentiment_scores.append(0.25)  # Stronger left bias
                    elif any(pattern in chunk.lower() for pattern in RIGHT_BIAS_PATTERNS['economic'] + RIGHT_BIAS_PATTERNS['social']):
                        sentiment_scores.append(0.75)  # Right bias
                    else:
                        sentiment_scores.append(0.5)  # Neutral
                else:
                    # Check if negative sentiment is about conservative issues
                    if any(pattern in chunk.lower() for pattern in RIGHT_BIAS_PATTERNS['economic'] + RIGHT_BIAS_PATTERNS['social']):
                        sentiment_scores.append(0.75)  # Right bias
                    elif any(pattern in chunk.lower() for pattern in LEFT_BIAS_PATTERNS['social'] + LEFT_BIAS_PATTERNS['environmental']):
                        sentiment_scores.append(0.25)  # Left bias
                    else:
                        sentiment_scores.append(0.5)  # Neutral
            
            if not sentiment_scores:
                return 0.5, 'Center'
            
            avg_score = np.mean(sentiment_scores)
            
            # More sensitive thresholds
            if avg_score < 0.35:
                return avg_score, 'Left'
            elif avg_score > 0.65:
                return avg_score, 'Right'
            else:
                return avg_score, 'Center'
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 0.5, 'Center'
    
    def analyze_loaded_language(self, text: str) -> Tuple[float, str]:
        """Detect loaded language that indicates bias"""
        text_lower = text.lower()
        
        loaded_scores = {}
        for category, phrases in LOADED_LANGUAGE.items():
            count = sum(1 for phrase in phrases if phrase in text_lower)
            loaded_scores[category] = count
        
        total_loaded = sum(loaded_scores.values())
        
        if total_loaded == 0:
            return 0.5, 'Center'
        
        # Weight different types of loaded language
        emotional_weight = loaded_scores.get('emotional', 0) * 0.4
        judgmental_weight = loaded_scores.get('judgmental', 0) * 0.6
        partisan_weight = loaded_scores.get('partisan', 0) * 1.0  # Highest weight
        
        total_weighted = emotional_weight + judgmental_weight + partisan_weight
        
        # Determine bias direction based on loaded language
        if 'radical left' in text_lower or 'socialist agenda' in text_lower or 'liberal elite' in text_lower:
            return 0.8, 'Right'
        elif 'far right' in text_lower or 'conservative agenda' in text_lower or 'republican agenda' in text_lower:
            return 0.2, 'Left'
        elif total_weighted > 1.5:  # Lower threshold
            # High loaded language suggests stronger bias
            if any(word in text_lower for word in ['corrupt', 'disastrous', 'terrible', 'horrible', 'evil']):
                return 0.75, 'Right'
            elif any(word in text_lower for word in ['greedy', 'selfish', 'exploiting', 'oppression']):
                return 0.25, 'Left'
            else:
                return 0.6, 'Right' if 'corrupt' in text_lower or 'disastrous' in text_lower else 'Left'
        elif total_weighted > 0.5:  # Lower threshold
            return 0.6, 'Right' if 'terrible' in text_lower or 'horrible' in text_lower else 'Left'
        else:
            return 0.5, 'Center'
    
    def _split_text_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks for analysis"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    current_chunk = [word]
                    current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def classify_bias(self, text: str) -> Tuple[float, str, Dict]:
        """Main bias classification function with detailed analysis"""
        if not text or len(text.strip()) < 10:
            return 0.5, 'Center', {'confidence': 'low', 'reason': 'insufficient_text'}
        
        # Get multiple bias indicators
        keyword_score, keyword_label, keyword_details = self.analyze_political_keywords(text)
        sentiment_score, sentiment_label = self.analyze_sentiment_context(text)
        loaded_score, loaded_label = self.analyze_loaded_language(text)
        
        # Make keyword analysis even more dominant
        final_score = (keyword_score * 0.8) + (sentiment_score * 0.15) + (loaded_score * 0.05)
        
        # Absolute rule: if left/right keyword score is very strong, force the label
        if keyword_details['left'] > 0.5:
            final_label = 'Left'
            final_score = min(final_score, 0.45)
        elif keyword_details['right'] > 0.5:
            final_label = 'Right'
            final_score = max(final_score, 0.7)
        else:
            # Lower left threshold further
            if final_score < 0.48:
                final_label = 'Left'
            elif final_score > 0.65:
                final_label = 'Right'
            else:
                final_label = 'Center'
        
        # Calculate confidence based on agreement between indicators
        indicators = [keyword_label, sentiment_label, loaded_label]
        agreement = max(indicators.count(label) for label in set(indicators))
        confidence = 'high' if agreement >= 2 else 'medium' if agreement >= 1 else 'low'
        
        # Add some randomness for more realistic results (but less than before)
        import random
        if random.random() < 0.05:  # 5% chance to adjust slightly
            final_score += random.uniform(-0.03, 0.03)
            final_score = max(0.0, min(1.0, final_score))
        
        analysis_details = {
            'keyword_score': keyword_score,
            'keyword_label': keyword_label,
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'loaded_score': loaded_score,
            'loaded_label': loaded_label,
            'confidence': confidence,
            'keyword_details': keyword_details
        }
        
        return final_score, final_label, analysis_details

# Initialize the analyzer
bias_analyzer = PoliticalBiasAnalyzer()

def classify_bias(text: str) -> Tuple[float, str]:
    """Legacy function for backward compatibility"""
    score, label, _ = bias_analyzer.classify_bias(text)
    return score, label 