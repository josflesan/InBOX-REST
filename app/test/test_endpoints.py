import os
import requests

def test_deliveries_test(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', 'test')
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert 'msg' in json
    assert json['msg'] == "I'm the test endpoint from blueprint_deliveries"

def test_deliveries_get(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323')
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert json['hashCode'] == "averysecurehash"

def test_deliveries_toggle_scanned(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323')
    response = requests.put(endpoint)
    assert response.status_code == 201

def test_deliveries_poll_scanned(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries', '63f52275b2422530719ec323', 'poll')
    response = requests.get(endpoint)
    assert response.status_code == 201

def test_deliveries_create(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'deliveries')
    response = requests.post(endpoint, json={"hashCode": "acoolhash", "userId": "2"})
    assert response.status_code == 201
