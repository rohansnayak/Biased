import pytest
import json
from backend.app import app, db, Article, Analysis

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_analyze_endpoint(client):
    """Test the analyze endpoint with text input"""
    response = client.post('/api/analyze', 
                          data={'raw_text': 'This is a test article about politics.'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'jobId' in data

def test_status_endpoint(client):
    """Test the status endpoint"""
    # First create an analysis
    with app.app_context():
        article = Article(user_id='test', raw_text='Test article')
        db.session.add(article)
        db.session.commit()
        analysis = Analysis(article_id=article.id)
        db.session.add(analysis)
        db.session.commit()
        
    response = client.get(f'/api/status/{analysis.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

def test_results_endpoint(client):
    """Test the results endpoint"""
    # First create an analysis with results
    with app.app_context():
        article = Article(user_id='test', raw_text='Test article')
        db.session.add(article)
        db.session.commit()
        analysis = Analysis(
            article_id=article.id,
            bias_score=0.5,
            bias_label='Center',
            sentiment_score=0.3,
            sentiment_label='Neutral'
        )
        db.session.add(analysis)
        db.session.commit()
        
    response = client.get(f'/api/results/{analysis.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'bias_score' in data
    assert 'sentiment_score' in data

def test_history_endpoint(client):
    """Test the history endpoint"""
    # First create some articles
    with app.app_context():
        article1 = Article(user_id='test', url='http://example.com/1')
        article2 = Article(user_id='test', url='http://example.com/2')
        db.session.add_all([article1, article2])
        db.session.commit()
        
    response = client.get('/api/history?userId=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2 