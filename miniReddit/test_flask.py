import pytest
from main import app # Flask instance of the API

def test_register():
    response = app.test_client().get('/register')
    assert response.status_code == 200

def test_create_complete():
    response = app.test_client().get('/11272744/create')
    assert response.status_code == 200

def test_profile_page():
    response = app.test_client().get('/11272744/profile/1')
    assert response.status_code == 200

def test_feed_page():
    response = app.test_client().get('/11272744/feed/1')
    assert response.status_code == 200