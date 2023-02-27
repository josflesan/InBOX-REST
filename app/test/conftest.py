import pytest
import os

TEST_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NzUwNDczOSwianRpIjoiYzZiM2RiNWYtNzBkOC00NmNjLTg4MzMtZmIyYjIwMTQ2NDAwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InJvb3QiLCJuYmYiOjE2Nzc1MDQ3MzksImV4cCI6MTY3NzUwNTYzOX0.oiK4XvNhCT_4QgIqGVX4m807U1HVu3r7k14L_lxUJnU"

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