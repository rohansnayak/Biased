from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import requests
from bs4 import BeautifulSoup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai')))
from analyze_text import analyze_text

app = Flask(__name__)
CORS(app)

# In-memory storage for testing
articles_db = {}
analysis_db = {}
job_counter = 0

def fetch_article_text(url):
    """Fetch and extract article text from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text from common article containers
        article_selectors = [
            'article', '[class*="article"]', '[class*="content"]', 
            '[class*="post"]', '[class*="story"]', 'main', '.entry-content'
        ]
        
        text = ""
        for selector in article_selectors:
            elements = soup.select(selector)
            if elements:
                text = ' '.join([elem.get_text().strip() for elem in elements])
                break
        
        # Fallback to body text if no article content found
        if not text:
            text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit text length
    except Exception as e:
        print(f"Error fetching article from {url}: {e}")
        return ""

def run_analysis_job(analysis_id):
    """Run analysis job (simplified for testing)"""
    global analysis_db
    analysis = analysis_db.get(analysis_id)
    if not analysis:
        return
    
    article_id = analysis['article_id']
    article = articles_db.get(article_id)
    if not article:
        return
    
    text = article['raw_text']
    if not text and article['url']:
        text = fetch_article_text(article['url'])
        if text:
            article['raw_text'] = text
    
    try:
        results = analyze_text(text or '')
        analysis['bias_score'] = results['bias_score']
        analysis['bias_label'] = results['bias_label']
        analysis['sentiment_score'] = results['sentiment_score']
        analysis['sentiment_label'] = results['sentiment_label']
        analysis['language_flags'] = results['language_flags']
        analysis['completed_at'] = time.time()
    except Exception as e:
        print(f"Error in analysis: {e}")
        # Fallback results
        analysis['bias_score'] = 0.5
        analysis['bias_label'] = 'Center'
        analysis['sentiment_score'] = 0.0
        analysis['sentiment_label'] = 'Neutral'
        analysis['language_flags'] = []
        analysis['completed_at'] = time.time()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global job_counter, articles_db, analysis_db
    
    user_id = request.form.get('userId', 'demo-user')
    url = request.form.get('url')
    file = request.files.get('file')
    raw_text = request.form.get('raw_text')
    
    if file:
        raw_text = file.read().decode('utf-8', errors='ignore')
    
    # Create article
    article_id = len(articles_db) + 1
    articles_db[article_id] = {
        'id': article_id,
        'user_id': user_id,
        'url': url,
        'raw_text': raw_text,
        'submitted_at': time.time()
    }
    
    # Create analysis
    job_counter += 1
    analysis_db[job_counter] = {
        'id': job_counter,
        'article_id': article_id,
        'bias_score': None,
        'bias_label': None,
        'sentiment_score': None,
        'sentiment_label': None,
        'language_flags': None,
        'completed_at': None
    }
    
    # Run analysis immediately for testing
    run_analysis_job(job_counter)
    
    return jsonify({'jobId': job_counter})

@app.route('/api/status/<int:job_id>', methods=['GET'])
def status(job_id):
    analysis = analysis_db.get(job_id)
    if not analysis:
        return jsonify({'status': 'not_found'}), 404
    return jsonify({'status': 'complete' if analysis['completed_at'] else 'pending'})

@app.route('/api/results/<int:job_id>', methods=['GET'])
def results(job_id):
    analysis = analysis_db.get(job_id)
    if not analysis:
        return jsonify({'error': 'not found'}), 404
    
    return jsonify({
        'bias_score': analysis['bias_score'] or 0.5,
        'bias_label': analysis['bias_label'] or 'Center',
        'sentiment_score': analysis['sentiment_score'] or 0.0,
        'sentiment_label': analysis['sentiment_label'] or 'Neutral',
        'language_flags': analysis['language_flags'] or [],
    })

@app.route('/api/history', methods=['GET'])
def history():
    user_id = request.args.get('userId', 'demo-user')
    history = []
    
    for article_id, article in articles_db.items():
        if article['user_id'] == user_id:
            analysis = None
            for analysis_id, analysis_data in analysis_db.items():
                if analysis_data['article_id'] == article_id:
                    analysis = analysis_data
                    break
            
            history.append({
                'id': article_id,
                'url': article['url'],
                'bias_label': analysis['bias_label'] if analysis else None,
                'sentiment_label': analysis['sentiment_label'] if analysis else None,
                'submitted_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(article['submitted_at'])),
            })
    
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 