"""Tests des services d'intégration API (Bloc4)."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from dashboard.services import DashboardService
from forecast.services import ForecastService


class TestDashboardService:
    @patch("dashboard.services.requests.post")
    def test_get_token_success(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "fake-token"},
        )

        service = DashboardService()
        token = service._get_token()
        assert token == "fake-token"

    @patch("dashboard.services.requests.post")
    def test_get_token_failure_raises(self, mock_post):
        mock_post.return_value = MagicMock(status_code=401)

        service = DashboardService()
        with pytest.raises(Exception, match="Échec auth Bloc1"):
            service._get_token()

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_trading_pair_success(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": 1, "base_currency_id": 1, "quote_currency_id": 2},
        )

        service = DashboardService()
        result = service.get_trading_pair("BTC", "USDT")
        assert result["id"] == 1

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_trading_pair_not_found(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(status_code=404)

        service = DashboardService()
        result = service.get_trading_pair("FAKE", "COIN")
        assert result is None

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_ohlcv_returns_list(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"date": "2025-01-01", "close": 45000}],
        )

        service = DashboardService()
        result = service.get_ohlcv(1, "daily")
        assert len(result) == 1

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_ohlcv_api_error_returns_empty(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(status_code=500)

        service = DashboardService()
        result = service.get_ohlcv(1, "daily")
        assert result == []

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_predictions_returns_list(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: [{"predicted_label": "UP", "confidence": 0.8}],
        )

        service = DashboardService()
        result = service.get_predictions(1, "daily")
        assert len(result) == 1

    @patch("dashboard.services.requests.post")
    def test_get_token_passes_timeout(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "fake-token"},
        )

        service = DashboardService()
        service._get_token()
        assert mock_post.call_args.kwargs["timeout"] == 10

    @patch("dashboard.services.requests.get")
    @patch("dashboard.services.requests.post")
    def test_get_ohlcv_passes_timeout(self, mock_post, mock_get):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "token"},
        )
        mock_get.return_value = MagicMock(status_code=200, json=lambda: [])

        service = DashboardService()
        service.get_ohlcv(1, "daily")
        assert mock_get.call_args.kwargs["timeout"] == 10


class TestForecastService:
    @patch("forecast.services.requests.post")
    def test_get_token_success(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "ml-token"},
        )

        service = ForecastService()
        token = service._get_token()
        assert token == "ml-token"

    @patch("forecast.services.requests.post")
    def test_get_token_failure_raises(self, mock_post):
        mock_post.return_value = MagicMock(status_code=401)

        service = ForecastService()
        with pytest.raises(Exception, match="Échec auth Bloc3"):
            service._get_token()

    @patch("forecast.services.requests.post")
    def test_get_classification_success(self, mock_post):
        responses = [
            MagicMock(status_code=200, json=lambda: {"access_token": "token"}),
            MagicMock(status_code=200, json=lambda: {
                "trading_pair_symbol": "BTC-USDT",
                "predictions": [{"predicted_label": "UP"}],
            }),
        ]
        mock_post.side_effect = responses

        service = ForecastService()
        result = service.get_classification("BTC-USDT", "daily")
        assert "predictions" in result

    @patch("forecast.services.requests.post")
    def test_get_classification_api_error(self, mock_post):
        responses = [
            MagicMock(status_code=200, json=lambda: {"access_token": "token"}),
            MagicMock(status_code=500, text="Internal Server Error"),
        ]
        mock_post.side_effect = responses

        service = ForecastService()
        result = service.get_classification("BTC-USDT", "daily")
        assert "error" in result

    @patch("forecast.services.requests.post")
    def test_get_classification_retries_once_on_expired_token(self, mock_post):
        responses = [
            MagicMock(status_code=200, json=lambda: {"access_token": "stale-token"}),
            MagicMock(status_code=401),
            MagicMock(status_code=200, json=lambda: {"access_token": "fresh-token"}),
            MagicMock(status_code=200, json=lambda: {"predictions": [{"predicted_label": "UP"}]}),
        ]
        mock_post.side_effect = responses

        service = ForecastService()
        result = service.get_classification("BTC-USDT", "daily")
        assert "predictions" in result
        assert mock_post.call_count == 4

    @patch("forecast.services.requests.post")
    def test_get_classification_network_error_returns_error_dict(self, mock_post):
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"access_token": "token"}),
            requests.exceptions.ConnectionError("boom"),
        ]

        service = ForecastService()
        result = service.get_classification("BTC-USDT", "daily")
        assert "error" in result
