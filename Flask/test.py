import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
def test_signin_success(client):
    login_data = {
        "email": "abcd@gmail.com",
        "password":"1234",
       
    }

    response = client.post('/signin', json=login_data)

    assert response.status_code == 200

    assert 'token' in response.json
    assert response.json['message'] == 'Login successful'
 
 
 
 
 