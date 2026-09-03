"""Fixtures partagées pour les tests Bloc1_data."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


os.environ["DB_USERNAME"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "test_db"
os.environ["API_E1_SECRET_KEY"] = "test-secret-key-for-unit-tests"
os.environ["API_E1_ALGORITHM"] = "HS256"


# Mock du module database avant tout import pour éviter la connexion PostgreSQL
_mock_engine = MagicMock()
_mock_session_class = MagicMock()
_mock_base = MagicMock()

_db_patch = patch.dict(sys.modules, {})


def _create_mock_database_module():
    """Crée un faux module src.C4_database.database pour éviter la connexion à la BDD."""
    mock_module = MagicMock()
    mock_module.engine = _mock_engine
    mock_module.Session = _mock_session_class
    mock_module.Base = _mock_base
    mock_module.with_session = lambda f: f
    mock_module.Database = MagicMock
    return mock_module


# Patch le module database dans sys.modules AVANT que quiconque l'importe
_mock_db_module = _create_mock_database_module()
sys.modules.setdefault("src.C4_database.database", _mock_db_module)


from fastapi.testclient import TestClient


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.password_hashed = "$2b$12$LJ3m4sMKfRzG.Y5E9QFYOeQYD9Hb/mC.1Fp5vK8xXkXNjF2Wd2Pq"
    user.role = "user"
    user.status = "active"
    return user


@pytest.fixture
def mock_script_user():
    user = MagicMock()
    user.id = 2
    user.username = "script_bot"
    user.password_hashed = "$2b$12$LJ3m4sMKfRzG.Y5E9QFYOeQYD9Hb/mC.1Fp5vK8xXkXNjF2Wd2Pq"
    user.role = "script"
    user.status = "active"
    return user


@pytest.fixture
def mock_db(mock_user, mock_script_user):
    db = MagicMock()
    db.users.get_by_username.side_effect = lambda u: {
        "testuser": mock_user,
        "script_bot": mock_script_user,
    }.get(u)
    db.trading_pairs.get_pairs_by_base_currency_symbol.return_value = []
    db.trading_pairs.get_pair_by_currency_symbols.return_value = None
    db.currencies.list_all.return_value = []
    db.exchanges.list_all.return_value = []
    db.ohlcv_daily.get_ohlcv_by_trading_pair.return_value = []
    db.ohlcv_hourly.get_ohlcv_by_trading_pair.return_value = []
    db.prediction_hourly.get_predictions_by_trading_pair.return_value = []
    db.prediction_daily.get_predictions_by_trading_pair.return_value = []
    db.prediction_hourly.get_last_prediction_by_trading_pair.return_value = None
    db.prediction_daily.get_last_prediction_by_trading_pair.return_value = None
    return db


@pytest.fixture
def app(mock_db):
    from src.C5_api.api import app as fastapi_app
    from src.C5_api.utils.deps import get_db

    def override_get_db():
        yield mock_db

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def auth_token():
    from src.C5_api.utils.auth import create_access_token
    return create_access_token(data={"sub": "testuser"})


@pytest.fixture
def script_token():
    from src.C5_api.utils.auth import create_access_token
    return create_access_token(data={"sub": "script_bot"})


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def script_headers(script_token):
    return {"Authorization": f"Bearer {script_token}"}
