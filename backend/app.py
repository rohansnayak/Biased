from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import time
from redis import Redis
from rq import Queue
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../ai')))
from analyze_text import analyze_text

app = Flask(__name__)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/biased')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Redis and RQ setup
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(redis_url)
queue = Queue('analysis', connection=redis_conn)

def run_analysis_job(analysis_id):
    with app.app_context():
        analysis = Analysis.query.get(analysis_id)
        if not analysis:
            return
        article = Article.query.get(analysis.article_id)
        if not article:
            return
        text = article.raw_text
        if not text and article.url:
            # TODO: Fetch and parse article from URL
            text = ''
        results = analyze_text(text or '')
        analysis.bias_score = results['bias_score']
        analysis.bias_label = results['bias_label']
        analysis.sentiment_score = results['sentiment_score']
        analysis.sentiment_label = results['sentiment_label']
        analysis.language_flags = results['language_flags']
        analysis.completed_at = db.func.now()
        db.session.commit()

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    url = db.Column(db.String)
    raw_text = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=db.func.now())
    analysis = db.relationship('Analysis', backref='article', uselist=False)

class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)
    bias_score = db.Column(db.Float)
    bias_label = db.Column(db.String)
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.String)
    language_flags = db.Column(db.JSON)
    completed_at = db.Column(db.DateTime)

with app.app_context():
    db.create_all()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    user_id = request.form.get('userId', 'demo-user')
    url = request.form.get('url')
    file = request.files.get('file')
    raw_text = None
    if file:
        raw_text = file.read().decode('utf-8', errors='ignore')
    article = Article(user_id=user_id, url=url, raw_text=raw_text)
    db.session.add(article)
    db.session.commit()
    analysis = Analysis(article_id=article.id)
    db.session.add(analysis)
    db.session.commit()
    # Enqueue analysis job
    queue.enqueue('app.run_analysis_job', analysis.id)
    return jsonify({'jobId': analysis.id})

@app.route('/api/status/<int:job_id>', methods=['GET'])
def status(job_id):
    analysis = Analysis.query.get(job_id)
    if not analysis:
        return jsonify({'status': 'not_found'}), 404
    return jsonify({'status': 'complete' if analysis.completed_at else 'pending'})

@app.route('/api/results/<int:job_id>', methods=['GET'])
def results(job_id):
    analysis = Analysis.query.get(job_id)
    if not analysis:
        return jsonify({'error': 'not found'}), 404
    return jsonify({
        'bias_score': analysis.bias_score or 0.3,
        'bias_label': analysis.bias_label or 'Center',
        'sentiment_score': analysis.sentiment_score or 0.1,
        'sentiment_label': analysis.sentiment_label or 'Neutral',
        'language_flags': analysis.language_flags or [
            {'snippet': 'shocking revelation'},
            {'snippet': 'unprecedented move'},
        ],
    })

@app.route('/api/history', methods=['GET'])
def history():
    user_id = request.args.get('userId', 'demo-user')
    articles = Article.query.filter_by(user_id=user_id).order_by(Article.submitted_at.desc()).all()
    history = []
    for article in articles:
        analysis = article.analysis
        history.append({
            'id': article.id,
            'url': article.url,
            'bias_label': analysis.bias_label if analysis else None,
            'sentiment_label': analysis.sentiment_label if analysis else None,
            'submitted_at': article.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 