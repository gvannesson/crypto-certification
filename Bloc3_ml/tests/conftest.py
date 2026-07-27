"""Fixtures partagées pour les tests Bloc3_ml."""

import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient


os.environ.setdefault("API_E1_BASE_URL", "http://localhost:8001")
os.environ.setdefault("API_E3_SECRET_KEY", "test-secret-key-for-ml-tests")
os.environ.setdefault("API_E3_ALGORITHM", "HS256")
os.environ.setdefault("API_E3_USERNAME", "ml_user")
os.environ.setdefault("API_E3_PASSWORD", "ml_password")
os.environ.setdefault("MODELS_DIR_PATH", "/tmp/test_models")


@pytest.fixture
def app():
    from src.api.api import app as fastapi_app
    yield fastapi_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_token():
    from src.api.utils.auth import create_access_token
    return create_access_token(data={"sub": "ml_user"})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
