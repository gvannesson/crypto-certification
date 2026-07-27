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
