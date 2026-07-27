"""Tests d'authentification de l'API ML (Bloc3)."""

from unittest.mock import patch


class TestLogin:
    def test_login_success(self, client):
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "ml_user", "password": "ml_password"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "ml_user", "password": "wrong_password"},
        )
        assert response.status_code == 401

    def test_login_empty_password(self, client):
        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "ml_user", "password": ""},
        )
        assert response.status_code in (401, 422)


class TestAuthProtection:
    def test_classify_without_token_returns_401(self, client):
        response = client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "BTC-USDT", "num_pred": 3},
        )
        assert response.status_code == 401

    def test_classify_with_invalid_token_returns_401(self, client):
        response = client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "BTC-USDT", "num_pred": 3},
            headers={"Authorization": "Bearer invalid.token"},
        )
        assert response.status_code == 401
