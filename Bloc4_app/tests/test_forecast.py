"""Tests de la vue de classification/prédiction (Bloc4)."""

import pytest
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestClassifyView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")
        self.client.login(username="testuser", password="TestPass123!")

    def test_classify_page_renders_with_form(self):
        response = self.client.get(reverse("classify"))
        assert response.status_code == 200
        assert b"form" in response.content

    @patch("forecast.views.ForecastService")
    def test_classify_post_success(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_classification.return_value = {
            "trading_pair_symbol": "BTC-USDT",
            "num_pred": 3,
            "predictions": [
                {"date": "2025-01-01 01:00:00", "predicted_class": 2, "predicted_label": "UP", "confidence": 0.78},
                {"date": "2025-01-01 02:00:00", "predicted_class": 1, "predicted_label": "STABLE", "confidence": 0.65},
                {"date": "2025-01-01 03:00:00", "predicted_class": 0, "predicted_label": "DOWN", "confidence": 0.72},
            ],
        }

        response = self.client.post(
            reverse("classify"),
            {"trading_pair": "BTC-USDT", "granularity": "hourly", "num_pred": "3"},
        )
        assert response.status_code == 200
        mock_service.get_classification.assert_called_once_with(
            trading_pair_symbol="BTC-USDT",
            granularity="hourly",
        )

    @patch("forecast.views.ForecastService")
    def test_classify_post_api_error(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_classification.return_value = {"error": "Erreur API : 500"}

        response = self.client.post(
            reverse("classify"),
            {"trading_pair": "BTC-USDT", "granularity": "daily", "num_pred": "1"},
        )
        assert response.status_code == 200

    @patch("forecast.views.ForecastService")
    def test_classify_post_connection_error(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.get_classification.side_effect = Exception("Connection refused")

        response = self.client.post(
            reverse("classify"),
            {"trading_pair": "BTC-USDT", "granularity": "daily", "num_pred": "1"},
        )
        assert response.status_code == 200

    def test_classify_post_invalid_form(self):
        response = self.client.post(
            reverse("classify"),
            {"trading_pair": "INVALID", "granularity": "daily", "num_pred": "1"},
        )
        assert response.status_code == 200

    def test_classify_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse("classify"))
        assert response.status_code == 302
        assert "/login/" in response.url
