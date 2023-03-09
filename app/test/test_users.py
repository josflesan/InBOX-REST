import os
import requests
import base64

API_TOKEN = ""

def test_user_registration_success(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'register')
    response = requests.post(endpoint, json={"email": "testemail@gmail.com", "password": "123verysecure"})
    assert response.status_code == 201
    json = response.json()
    assert json['result']

def test_user_registration_fail(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'register')
    response = requests.post(endpoint, json={"email": "testemail@gmail.com", "password": "gottatryitig"})
    assert response.status_code == 401
    json = response.json()
    assert not json['result']

def test_user_login_success(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"email": "testemail@gmail.com", "password": "123verysecure"})
    assert response.status_code == 201
    json = response.json()
    assert json['token']

    global API_TOKEN
    API_TOKEN = json['token']  # Obtain current API token

def test_user_login_failed(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"email": "fakeuser@gmail.com", "password": "123verysecure"})
    assert response.status_code == 401
    json = response.json()
    assert not json['result']

def test_user_get(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'query')
    response = requests.post(endpoint, json={"email": "testemail@gmail.com", "password": "123verysecure"}, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json["email"] == "testemail@gmail.com"

def test_user_modify(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'query')
    response = requests.put(endpoint, json={"email": "testemail@gmail.com", "password": "123verysecure", "updates": {"email": "anewuser@gmail.com"}}, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json["result"]

    # Revert changes to the test user
    endpoint = os.path.join(api_v1_host, 'users', 'query')
    response = requests.put(endpoint, json={"email": "anewuser@gmail.com", "password": "123verysecure", "updates": {"email": "testemail@gmail.com"}}, headers={"Authorization": f"Bearer {API_TOKEN}"})

def test_user_logout(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'users', 'logout', 'testemail@gmail.com')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_TOKEN}"})
    assert response.status_code == 201
    json = response.json()
    assert json['result']

def test_user_elevate(api_v1_host):
    # Login with admin account
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"email": "suchanemail@gmail.com", "password": "suchasecurepassword"})
    assert response.status_code == 201

    admin_api_key = response.json()["token"]

    # Make request using admin account
    endpoint = os.path.join(api_v1_host, 'users', 'elevate', 'testemail@gmail.com')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {admin_api_key}"})
    print(response.json())
    assert response.status_code == 201
    assert response.json()["result"]

def test_user_delete(api_v1_host):
    # Login with admin account
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"email": "suchanemail@gmail.com", "password": "suchasecurepassword"})
    assert response.status_code == 201

    admin_api_key = response.json()["token"]

    # Try to delete testuser
    endpoint = os.path.join(api_v1_host, 'users', 'delete')
    response = requests.delete(endpoint, json={"email": "testemail@gmail.com"}, headers={"Authorization": f"Bearer {admin_api_key}"})
    assert response.status_code == 201
