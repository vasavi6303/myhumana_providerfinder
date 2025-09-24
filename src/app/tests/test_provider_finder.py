import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'

def test_search_mock():
    r = client.post('/search', json={'query': 'cardiology', 'location': '37203'})
    assert r.status_code == 200
    body = r.json()
    assert 'providers' in body
    assert body['count'] >= 1
