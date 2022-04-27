import pytest
from main import app # Flask instance of the API

def test_register():
    response = app.test_client().get('/register')
    assert response.status_code == 200

def test_upload():
    response = app.test_client().get('/upload')
    assert response.status_code == 200

def test_frontpage():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_machine_learning_data():
    response = app.test_client().get('/mldata')
    assert response.status_code == 200

def test_oneclick():
    response = app.test_client().get('/oneclick')
    assert response.status_code == 200