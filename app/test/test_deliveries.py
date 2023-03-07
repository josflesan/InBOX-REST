import os
import requests
import base64

API_ADMIN_KEY= ""

def login(api_v1_host):
    # Login using admin user
    endpoint = os.path.join(api_v1_host, 'users', 'login')
    response = requests.post(endpoint, json={"username": "anadminaccount", "password": "suchasecurepassword"})
    global API_ADMIN_KEY
    API_ADMIN_KEY = response.json()["token"]

def test_deliveries_test(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', 'test')
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert 'msg' in json
    assert json['msg'] == "I'm the test endpoint from blueprint_deliveries"

def test_deliveries_get(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 200
    json = response.json()
    assert json['hashCode'] == "averysecurehash"

def test_deliveries_check_hash(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323', 'averysecurehash')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 201
    json = response.json()
    assert json['result']

def test_deliveries_toggle_scanned(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323')
    response = requests.put(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 201

def test_deliveries_poll_scanned(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323', 'poll')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 201

def test_deliveries_update_delivered(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323', 'delivered')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 201
    assert response.json()['result']

def test_deliveries_get_image(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323', 'image')
    response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"})
    assert response.status_code == 201
    image_data = base64.b64decode(response.json()['result'])
    with open("testImage.png", "wb") as fh:
        fh.write(image_data)

def test_deliveries_create(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries')
    response = requests.post(endpoint, headers={"Authorization": f"Bearer {API_ADMIN_KEY}"}, json={"hashCode": "acoolhash", "userId": "2"})
    assert response.status_code == 201
