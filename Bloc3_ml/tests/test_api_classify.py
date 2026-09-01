"""Tests des endpoints de classification de l'API ML (Bloc3)."""

from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd


def _mock_model(predicted_class, proba):
    """Mock XGBoost minimal mais fidèle sur le point qui piège un MagicMock nu :
    model.get_booster().feature_names doit être None (pas un MagicMock auto-généré,
    qui est itérable-vide et ferait silencieusement tomber feature_cols à [] dans
    _run_classification, donnant un DataFrame à 0 colonne -> row.empty -> [] renvoyé).
    """
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([predicted_class])
    mock_model.predict_proba.return_value = np.array([proba])
    mock_model.get_booster.return_value.feature_names = None
    return mock_model


def _sample_ohlcv(periods, freq):
    dates = pd.date_range("2025-01-01", periods=periods, freq=freq)
    return pd.DataFrame({
        "date": dates,
        "open": np.random.uniform(40000, 50000, periods),
        "high": np.random.uniform(50000, 55000, periods),
        "low": np.random.uniform(38000, 40000, periods),
        "close": np.random.uniform(40000, 50000, periods),
        "volume_quote": np.random.uniform(1e6, 1e8, periods),
        "trading_pair_id": 1,
    })


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
        mock_load_model.return_value = _mock_model(2, [0.1, 0.2, 0.7])
        mock_fetch_ohlcv.return_value = _sample_ohlcv(100, "D")

        response = client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "BTC-USDT"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["trading_pair_symbol"] == "BTC-USDT"
        assert len(body["predictions"]) >= 1
        pred = body["predictions"][0]
        assert "predicted_class" in pred
        assert "predicted_label" in pred
        assert "confidence" in pred
        assert "date" in pred

    @patch("src.api.routes.classify.fetch_recent_ohlcv")
    @patch("src.api.routes.classify.load_model")
    def test_classify_hourly_success(self, mock_load_model, mock_fetch_ohlcv, client, auth_headers):
        mock_load_model.return_value = _mock_model(0, [0.6, 0.3, 0.1])
        mock_fetch_ohlcv.return_value = _sample_ohlcv(200, "h")

        response = client.post(
            "/api/v1/classify/classify_hourly",
            json={"trading_pair_symbol": "BTC-USDT"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["trading_pair_symbol"] == "BTC-USDT"
        assert len(body["predictions"]) >= 1

    @patch("src.api.routes.classify.fetch_recent_ohlcv")
    @patch("src.api.routes.classify.load_model")
    def test_classify_ignores_unknown_extra_fields(self, mock_load_model, mock_fetch_ohlcv, client, auth_headers):
        # ClassifyRequest (src/api/utils/classes.py) ne déclare que trading_pair_symbol :
        # Pydantic ignore silencieusement les champs inconnus par défaut (pas de
        # model_config extra="forbid"). Documente ce comportement explicitement plutôt
        # que de laisser un client croire qu'un paramètre non supporté serait validé.
        mock_load_model.return_value = _mock_model(1, [0.2, 0.6, 0.2])
        mock_fetch_ohlcv.return_value = _sample_ohlcv(100, "D")

        response = client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "BTC-USDT", "num_pred": 30},
            headers=auth_headers,
        )
        assert response.status_code == 200

    @patch("src.api.routes.classify.load_model")
    def test_classify_model_not_found_returns_error(self, mock_load_model, app, auth_headers):
        from fastapi.testclient import TestClient

        mock_load_model.side_effect = FileNotFoundError("Modèle introuvable")

        error_client = TestClient(app, raise_server_exceptions=False)
        response = error_client.post(
            "/api/v1/classify/classify_daily",
            json={"trading_pair_symbol": "FAKE-PAIR"},
            headers=auth_headers,
        )
        assert response.status_code == 500

    def test_classify_missing_body(self, client, auth_headers):
        response = client.post(
            "/api/v1/classify/classify_daily",
            headers=auth_headers,
        )
        assert response.status_code == 422
