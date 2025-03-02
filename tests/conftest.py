import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_password():
    return "strong-test-pass-123!"

@pytest.fixture
def test_user(test_password):
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password=test_password
    )
    return user

@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client