import pytest
from unittest.mock import patch

def test_health_check(app_client):
    """Test /health endpoint returns 200 with status healthy."""
    response = app_client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'model_loaded' in data
    assert 'encoder_loaded' in data

def test_models_list(app_client):
    """Test /models returns the correct model info."""
    response = app_client.get('/models')
    assert response.status_code == 200
    data = response.get_json()
    assert 'available_models' in data
    assert 'current_model' in data
    assert 'diseases_count' in data
    assert data['diseases_count'] > 0

def test_home_page(app_client):
    """Test / serves the HTML template."""
    response = app_client.get('/')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()

def test_about_page(app_client):
    """Test /about serves the HTML template."""
    response = app_client.get('/about')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()

def test_contact_page(app_client):
    """Test /contact serves the HTML template."""
    response = app_client.get('/contact')
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()
