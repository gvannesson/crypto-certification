"""Tests d'authentification et de gestion des comptes (Bloc4)."""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        assert response.status_code == 200
        assert b"form" in response.content

    def test_login_success_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "TestPass123!"},
        )
        assert response.status_code == 302
        assert "/dashboard/" in response.url

    def test_login_wrong_password_stays_on_page(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "wrong"},
        )
        assert response.status_code == 200

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get(reverse("login"))
        assert response.status_code == 302
        assert "/dashboard/" in response.url


@pytest.mark.django_db
class TestRegister(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_page_renders(self):
        response = self.client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_success_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {"username": "newuser", "password1": "Str0ngP@ss!", "password2": "Str0ngP@ss!"},
        )
        assert response.status_code == 302
        assert User.objects.filter(username="newuser").exists()

    def test_register_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {"username": "newuser", "password1": "Pass123!", "password2": "Different123!"},
        )
        assert response.status_code == 200
        assert not User.objects.filter(username="newuser").exists()

    def test_register_duplicate_username(self):
        User.objects.create_user(username="existing", password="Pass123!")
        response = self.client.post(
            reverse("register"),
            {"username": "existing", "password1": "Str0ngP@ss!", "password2": "Str0ngP@ss!"},
        )
        assert response.status_code == 200
        assert User.objects.filter(username="existing").count() == 1


@pytest.mark.django_db
class TestLogout(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="TestPass123!")

    def test_logout_redirects_to_login(self):
        self.client.login(username="testuser", password="TestPass123!")
        response = self.client.get(reverse("logout"))
        assert response.status_code == 302

    def test_logout_clears_session(self):
        self.client.login(username="testuser", password="TestPass123!")
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/login/" in response.url


@pytest.mark.django_db
class TestAccessControl(TestCase):
    def setUp(self):
        self.client = Client()

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_charts_requires_authentication(self):
        response = self.client.get(reverse("charts"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_classify_requires_authentication(self):
        response = self.client.get(reverse("classify"))
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_index_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse("index"))
        assert response.status_code == 302
        assert "/login/" in response.url
