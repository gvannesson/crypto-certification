"""Tests d'authentification et d'autorisation de l'API Bloc1."""

import pytest
from unittest.mock import patch


class TestLogin:
    def test_login_success(self, client, mock_db, mock_user):
        mock_db.users.get_by_username.return_value = mock_user

        with patch("src.C5_api.routes.login.verify_password", return_value=True):
            response = client.post(
                "/api/v1/authentification/login",
                data={"username": "testuser", "password": "correct_password"},
            )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["role"] == "user"

    def test_login_wrong_password(self, client, mock_db, mock_user):
        mock_db.users.get_by_username.return_value = mock_user

        with patch("src.C5_api.routes.login.verify_password", return_value=False):
            response = client.post(
                "/api/v1/authentification/login",
                data={"username": "testuser", "password": "wrong"},
            )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_unknown_user(self, client, mock_db):
        mock_db.users.get_by_username.return_value = None

        response = client.post(
            "/api/v1/authentification/login",
            data={"username": "unknown", "password": "anything"},
        )

        assert response.status_code == 401

    def test_register_success(self, client, mock_db):
        mock_db.users.get_by_username.return_value = None
        new_user = type("User", (), {"id": 10, "username": "newuser", "role": "user"})()
        mock_db.users.create.return_value = new_user

        response = client.post(
            "/api/v1/authentification/register",
            json={"username": "newuser", "password": "securepass123"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["username"] == "newuser"
        assert body["role"] == "user"

    def test_register_duplicate_user(self, client, mock_db, mock_user):
        mock_db.users.get_by_username.return_value = mock_user

        response = client.post(
            "/api/v1/authentification/register",
            json={"username": "testuser", "password": "password"},
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestUserProfile:
    def test_get_current_user_profile(self, client, auth_headers, mock_user):
        response = client.get("/api/v1/authentification/me", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["username"] == "testuser"
        assert body["role"] == "user"
        assert body["status"] == "active"

    def test_get_profile_without_token_returns_401(self, client):
        response = client.get("/api/v1/authentification/me")
        assert response.status_code == 401

    def test_update_password_success(self, client, auth_headers, mock_db):
        with patch("src.C5_api.routes.login.verify_password", return_value=True):
            response = client.put(
                "/api/v1/authentification/password",
                json={"current_password": "oldpass", "new_password": "newpass123"},
                headers=auth_headers,
            )

        assert response.status_code == 200
        assert "updated" in response.json()["message"].lower()
        mock_db.users.update.assert_called_once()

    def test_update_password_wrong_current(self, client, auth_headers):
        with patch("src.C5_api.routes.login.verify_password", return_value=False):
            response = client.put(
                "/api/v1/authentification/password",
                json={"current_password": "wrong", "new_password": "newpass123"},
                headers=auth_headers,
            )

        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    def test_delete_account_success(self, client, auth_headers, mock_db):
        response = client.delete("/api/v1/authentification/account", headers=auth_headers)

        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        mock_db.users.delete.assert_called_once()

    def test_delete_account_without_token_returns_401(self, client):
        response = client.delete("/api/v1/authentification/account")
        assert response.status_code == 401


class TestAuthProtection:
    def test_endpoint_without_token_returns_401(self, client):
        response = client.get("/api/v1/ohlcv/daily_by_trading_pair_id", params={"trading_pair_id": 1})
        assert response.status_code == 401

    def test_endpoint_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/api/v1/ohlcv/daily_by_trading_pair_id",
            params={"trading_pair_id": 1},
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_endpoint_with_valid_token_succeeds(self, client, auth_headers):
        response = client.get(
            "/api/v1/ohlcv/daily_by_trading_pair_id",
            params={"trading_pair_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_script_only_endpoint_with_user_role_returns_403(self, client, auth_headers):
        response = client.post(
            "/api/v1/predictions/hourly",
            json={"trading_pair_id": 1, "date": "2025-01-01T00:00:00", "predicted_class": 2, "predicted_label": "UP"},
            headers=auth_headers,
        )
        assert response.status_code == 403

    def test_script_only_endpoint_with_script_role_succeeds(self, client, script_headers, mock_db):
        mock_obj = type("Pred", (), {
            "id": 1, "trading_pair_id": 1, "date": "2025-01-01",
            "predicted_class": 2, "predicted_label": "UP", "confidence": 0.85, "model_name": "xgb"
        })()
        mock_db.prediction_hourly.create.return_value = mock_obj

        response = client.post(
            "/api/v1/predictions/hourly",
            json={"trading_pair_id": 1, "date": "2025-01-01T00:00:00", "predicted_class": 2, "predicted_label": "UP"},
            headers=script_headers,
        )
        assert response.status_code == 200
