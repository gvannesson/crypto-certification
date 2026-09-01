"""Tests des vues dashboard (Bloc4)."""

import pytest
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    @patch("dashboard.views.DashboardService")
    def test_dashboard_renders_successfully(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 1}
        mock_service.get_predictions.return_value = [{"predicted_label": "UP", "confidence": 0.85}]
        mock_service.get_ohlcv.return_value = [{"close": 45000.0}]

        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 200

    @patch("dashboard.views.DashboardService")
    def test_dashboard_handles_no_trading_pair(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = None

        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 200

    @patch("dashboard.views.DashboardService")
    def test_dashboard_handles_empty_predictions(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 1}
        mock_service.get_predictions.return_value = []
        mock_service.get_ohlcv.return_value = []

        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestMonitoringView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    @patch("dashboard.views.DashboardService")
    def test_monitoring_renders_with_evaluable_predictions(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 156}
        mock_service.get_predictions.return_value = [
            {"date": "2026-01-02T00:00:00", "predicted_label": "UP", "model_name": "xgboost"},
        ]
        mock_service.get_ohlcv.return_value = [
            {"date": "2026-01-01T00:00:00", "close": 100},
            {"date": "2026-01-02T00:00:00", "close": 101},
        ]

        response = self.client.get(reverse("monitoring"))
        assert response.status_code == 200
        assert "xgboost" in response.content.decode()

    @patch("dashboard.views.DashboardService")
    def test_monitoring_handles_no_evaluable_predictions(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 156}
        mock_service.get_predictions.return_value = [
            {"date": "2026-12-31T00:00:00", "predicted_label": "UP", "model_name": "xgboost"},
        ]
        mock_service.get_ohlcv.return_value = []

        response = self.client.get(reverse("monitoring"))
        assert response.status_code == 200
        assert "Aucune prédiction évaluable" in response.content.decode()

    def test_monitoring_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse("monitoring"))
        assert response.status_code == 302

    @patch("dashboard.views.DashboardService")
    def test_monitoring_granularity_param_passed_through(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 156}
        mock_service.get_predictions.return_value = []
        mock_service.get_ohlcv.return_value = []

        response = self.client.get(reverse("monitoring"), {"granularity": "daily"})
        assert response.status_code == 200
        mock_service.get_predictions.assert_called_with(156, "daily")


@pytest.mark.django_db
class TestChartsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    def test_charts_page_renders(self):
        response = self.client.get(reverse("charts"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestChartDataAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    @patch("dashboard.views.DashboardService")
    def test_chart_data_returns_json(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = {"id": 1}
        mock_service.get_ohlcv.return_value = [{"date": "2025-01-01", "close": 45000}]
        mock_service.get_predictions.return_value = []

        response = self.client.get(
            reverse("api_chart_data"),
            {"base": "BTC", "quote": "USDT", "granularity": "daily"},
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"
        data = response.json()
        assert "ohlcv" in data
        assert "predictions" in data

    @patch("dashboard.views.DashboardService")
    def test_chart_data_pair_not_found(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_trading_pair.return_value = None

        response = self.client.get(
            reverse("api_chart_data"),
            {"base": "FAKE", "quote": "COIN"},
        )
        assert response.status_code == 404

    def test_chart_data_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse("api_chart_data"))
        assert response.status_code == 302
