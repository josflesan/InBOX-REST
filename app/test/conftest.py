import pytest
import os

# API Key Expires in 30 days
# Last refreshed 27/02/23
TEST_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NzUyMTA1MSwianRpIjoiOWZhMzc1MjgtZjRlZC00NThhLWIwNjEtZTM0MjExM2Q5NDgwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InJvb3QiLCJuYmYiOjE2Nzc1MjEwNTEsImV4cCI6MTY4MDExMzA1MX0.Tr-al1xm4mQ4vgBpVD6PgmHy9uPnDxRfMSY93nrOYWk"

def pytest_addoption(parser):
    # Ability to test API on different hosts
    parser.addoption("--host", action="store", default="http://localhost:5000")

@pytest.fixture(scope="session")
def host(request):
    return request.config.getoption("--host")

@pytest.fixture(scope="session")
def api_v1_host(host):
    return os.path.join(host, "api", "v1")

@pytest.fixture(scope="session")
def api_key():
    return TEST_API_KEY