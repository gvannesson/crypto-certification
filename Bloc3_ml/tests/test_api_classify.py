"""Tests des endpoints de classification de l'API ML (Bloc3)."""

from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd


class TestClassifyEndpoints:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "ML API is running" in response.json()["message"]

    @patch("src.api.routes.classify.fetch_recent_ohlcv")
    @patch("src.api.routes.classify.load_model")
    def test_classify_daily_success(self, mock_load_model, mock_fetch_ohlcv, client, auth_headers):
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([2])
        mock_model.predict_proba.return_value = np.array([[0.1, 0.2, 0.7]])
        mock_load_model.return_value = mock_model

        dates = pd.date_range("2025-01-01", periods=100, freq="D")
        df = pd.DataFrame({
            "date": dates,
            "open": np.random.uniform(40000, 50000, 100),
            "high": np.random.uniform(50000, 55000, 100),
            "low": np.random.uniform(38000, 40000, 100),
            "close": np.random.uniform(40000, 50000, 100),
            "volume_quote": np.random.uniform(1e6, 1e8, 100),
            "trading_pair_id": 1,
        })
        mock_fetch_ohlcv.return_value = df

        response = client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "BTC-USDT", "num_pred": 1},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["trading_pair_symbol"] == "BTC-USDT"
        assert body["num_pred"] == 1
        assert len(body["predictions"]) >= 1
        pred = body["predictions"][0]
        assert "predicted_class" in pred
        assert "predicted_label" in pred
        assert "confidence" in pred
        assert "date" in pred

    @patch("src.api.routes.classify.fetch_recent_ohlcv")
    @patch("src.api.routes.classify.load_model")
    def test_classify_hourly_success(self, mock_load_model, mock_fetch_ohlcv, client, auth_headers):
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0])
        mock_model.predict_proba.return_value = np.array([[0.6, 0.3, 0.1]])
        mock_load_model.return_value = mock_model

        dates = pd.date_range("2025-01-01", periods=200, freq="h")
        df = pd.DataFrame({
            "date": dates,
            "open": np.random.uniform(40000, 50000, 200),
            "high": np.random.uniform(50000, 55000, 200),
            "low": np.random.uniform(38000, 40000, 200),
            "close": np.random.uniform(40000, 50000, 200),
            "volume_quote": np.random.uniform(1e6, 1e8, 200),
            "trading_pair_id": 1,
        })
        mock_fetch_ohlcv.return_value = df

        response = client.post(
            "/api/v1/classify/classify_hourly",
            json={"trading_pair_symbol": "BTC-USDT", "num_pred": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["num_pred"] == 3

    def test_classify_daily_invalid_num_pred(self, client, auth_headers):
        with patch("src.api.routes.classify.load_model"):
            response = client.post(
                "/api/v1/classify/classify_daily",
                json={"trading_pair_symbol": "BTC-USDT", "num_pred": 30},
                headers=auth_headers,
            )
        assert response.status_code == 400
        assert "num_pred" in response.json()["detail"]

    def test_classify_hourly_invalid_num_pred(self, client, auth_headers):
        with patch("src.api.routes.classify.load_model"):
            response = client.post(
                "/api/v1/classify/classify_hourly",
                json={"trading_pair_symbol": "BTC-USDT", "num_pred": 50},
                headers=auth_headers,
            )
        assert response.status_code == 400

    @patch("src.api.routes.classify.load_model")
    def test_classify_model_not_found_returns_error(self, mock_load_model, app, auth_headers):
        from fastapi.testclient import TestClient

        mock_load_model.side_effect = FileNotFoundError("Modèle introuvable")

        error_client = TestClient(app, raise_server_exceptions=False)
        response = error_client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "FAKE-PAIR", "num_pred": 1},
            headers=auth_headers,
        )
        assert response.status_code == 500

    def test_classify_missing_body(self, client, auth_headers):
        response = client.post(
            "/api/v1/classify/classify_daily",
            headers=auth_headers,
        )
        assert response.status_code == 422
