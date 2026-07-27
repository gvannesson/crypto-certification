"""Tests des endpoints de l'API Bloc1 (OHLCV, trading_pairs, predictions)."""

from unittest.mock import MagicMock
from datetime import datetime


class TestHealthAndRoot:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Bloc1 Data API is running" in response.json()["message"]

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestTradingPairs:
    def test_get_trading_pairs_by_symbol(self, client, auth_headers, mock_db):
        mock_pair = MagicMock()
        mock_pair.id = 1
        mock_pair.base_currency_id = 1
        mock_pair.quote_currency_id = 2
        mock_db.trading_pairs.get_pairs_by_base_currency_symbol.return_value = [mock_pair]

        response = client.get(
            "/api/v1/trading_pairs/all",
            params={"symbol": "BTC"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        mock_db.trading_pairs.get_pairs_by_base_currency_symbol.assert_called_once_with("BTC")

    def test_get_trading_pair_by_currency_symbols(self, client, auth_headers, mock_db):
        mock_pair = MagicMock()
        mock_pair.id = 1
        mock_db.trading_pairs.get_pair_by_currency_symbols.return_value = mock_pair

        response = client.get(
            "/api/v1/trading_pairs/trading_pair_by_currency_symbols",
            params={"base": "btc", "quote": "usdt"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        mock_db.trading_pairs.get_pair_by_currency_symbols.assert_called_once_with("BTC", "USDT")

    def test_get_trading_pair_not_found(self, client, auth_headers, mock_db):
        mock_db.trading_pairs.get_pair_by_currency_symbols.return_value = None

        response = client.get(
            "/api/v1/trading_pairs/trading_pair_by_currency_symbols",
            params={"base": "XYZ", "quote": "ABC"},
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestOHLCV:
    def test_get_ohlcv_daily(self, client, auth_headers, mock_db):
        mock_db.ohlcv_daily.get_ohlcv_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/ohlcv/daily_by_trading_pair_id",
            params={"trading_pair_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_ohlcv_hourly(self, client, auth_headers, mock_db):
        mock_db.ohlcv_hourly.get_ohlcv_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/ohlcv/hourly_by_trading_pair_id",
            params={"trading_pair_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_ohlcv_minute(self, client, auth_headers, mock_db):
        mock_db.ohlcv_minute.get_ohlcv_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/ohlcv/minute_by_trading_pair_id",
            params={"trading_pair_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_ohlcv_daily_with_start_date(self, client, auth_headers, mock_db):
        mock_db.ohlcv_daily.get_ohlcv_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/ohlcv/daily_by_trading_pair_id",
            params={"trading_pair_id": 1, "start_date": "2024-01-01"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        mock_db.ohlcv_daily.get_ohlcv_by_trading_pair.assert_called_once_with(1, "2024-01-01")


class TestPredictions:
    def test_get_predictions_hourly(self, client, auth_headers, mock_db):
        mock_db.prediction_hourly.get_predictions_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/predictions/hourly_by_trading_pair_id/1",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_predictions_daily(self, client, auth_headers, mock_db):
        mock_db.prediction_daily.get_predictions_by_trading_pair.return_value = []

        response = client.get(
            "/api/v1/predictions/daily_by_trading_pair_id/1",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_last_prediction_hourly(self, client, auth_headers, mock_db):
        mock_db.prediction_hourly.get_last_prediction_by_trading_pair.return_value = None

        response = client.get(
            "/api/v1/predictions/last_hourly_by_trading_pair_id/1",
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_get_last_prediction_daily(self, client, auth_headers, mock_db):
        mock_db.prediction_daily.get_last_prediction_by_trading_pair.return_value = None

        response = client.get(
            "/api/v1/predictions/last_daily_by_trading_pair_id/1",
            headers=auth_headers,
        )
        assert response.status_code == 200
