import pytest
import json
import io
from app import create_app
from database import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_health_endpoint(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['database'] == 'connected'
    assert 'modules' in data

def test_page_renders(client):
    pages = [
        '/',
        '/dashboard',
        '/crop-recommendation',
        '/disease-detection',
        '/weather',
        '/chatbot',
        '/advisory'
    ]
    for p in pages:
        res = client.get(p)
        assert res.status_code == 200, f"Page {p} returned status {res.status_code}"

def test_crop_recommendation_api(client):
    payload = {
        'nitrogen': 90,
        'phosphorus': 42,
        'potassium': 43,
        'temperature': 20.88,
        'humidity': 82.0,
        'ph': 6.5,
        'rainfall': 202.9,
        'location': 'Test Andhra Region'
    }
    res = client.post('/api/crop/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['data']['recommended_crop'].lower() == 'rice'
    assert 'record_id' in data['data']

def test_chatbot_api(client):
    payload = {
        'message': 'When to irrigate maize crop?',
        'language': 'en'
    }
    res = client.post('/api/chatbot/message', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['data']['intent'] == 'irrigation_query'

def test_advisory_api(client):
    payload = {
        'crop_name': 'Tomato',
        'growth_stage': 'Flowering',
        'soil': {'nitrogen': 50, 'phosphorus': 40, 'potassium': 40, 'ph': 6.5},
        'weather': {'temperature': 27.0, 'humidity': 80.0, 'wind_speed_kmh': 10.0},
        'disease': {'predicted_disease': 'Early Blight', 'is_healthy': False}
    }
    res = client.post('/api/advisory/generate', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'irrigation_advice' in data['data']
    assert 'fertilizer_advice' in data['data']

def test_dashboard_stats_api(client):
    res = client.get('/api/dashboard/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'stats' in data
    assert 'recent_activities' in data
    assert 'charts' in data

def test_history_endpoints(client):
    res_crop = client.get('/api/history/crops')
    assert res_crop.status_code == 200
    res_dis = client.get('/api/history/diseases')
    assert res_dis.status_code == 200
    res_adv = client.get('/api/history/advisories')
    assert res_adv.status_code == 200

