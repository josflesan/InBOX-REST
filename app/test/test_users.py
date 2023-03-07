import os
import requests
import base64

API_TOKEN = ""

def test_user_registration_success(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'register')
    response = requests.post(endpoint, json={"username": "testuser", "email": "testemail@gmail.com", "password": "123verysecure"})
    assert response.status_code == 201
    json = response.json()
    assert json['result']

def test_user_registration_fail(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'register')
    response = requests.post(endpoint, json={"username": "testuser", "email": "tryingitagain@gmail.com", "password": "gottatryitig"})
    assert response.status_code == 401
    json = response.json()
    assert not json['result']

def test_user_login_success(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"username": "testuser", "password": "123verysecure"})
    assert response.status_code == 201
    json = response.json()
    assert json['token']

    global API_TOKEN
    API_TOKEN = json['token']  # Obtain current API token

def test_user_login_failed(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"username": "fakeuser", "password": "123verysecure"})
    assert response.status_code == 401
    json = response.json()
    assert not json['result']

def test_user_get(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'testuser')
    response = requests.post(endpoint, json={"username": "testuser", "password": "123verysecure"}, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json["username"] == "testuser"

def test_user_modify(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'testuser')
    response = requests.put(endpoint, json={"username": "testuser", "password": "123verysecure", "updates": {"username": "anewuser"}}, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json["result"]

    # Revert changes to the test user
    endpoint = os.path.join(api_v1_host, 'users', 'anewuser')
    response = requests.put(endpoint, json={"username": "anewuser", "password": "123verysecure", "updates": {"username": "testuser"}}, headers={"Authorization": f"Bearer {API_TOKEN}"})

def test_user_logout(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'logout', 'testuser')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json['result']

def test_user_elevate(api_v1_host, api_key):
    endpoint = os.path.join(api_v1_host, 'users', 'elevate', 'testuser')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    assert response.json()["result"]
