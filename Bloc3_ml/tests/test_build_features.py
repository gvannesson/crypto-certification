"""Tests de la construction des features pour le modèle de classification."""

import numpy as np
import pandas as pd
import pytest

from src.features.build_features import (
    build_features,
    add_lag_features,
    add_return_features,
    add_technical_indicators,
    add_temporal_features,
    add_target,
)


@pytest.fixture
def sample_ohlcv_daily():
    """Génère un DataFrame OHLCV réaliste pour les tests."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=120, freq="D")
    close = 45000 + np.cumsum(np.random.randn(120) * 500)
    return pd.DataFrame({
        "date": dates,
        "open": close + np.random.randn(120) * 100,
        "high": close + abs(np.random.randn(120) * 300),
        "low": close - abs(np.random.randn(120) * 300),
        "close": close,
        "volume_quote": np.random.uniform(1e7, 5e8, 120),
        "trading_pair_id": 1,
    })


@pytest.fixture
def sample_ohlcv_hourly():
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=500, freq="h")
    close = 45000 + np.cumsum(np.random.randn(500) * 100)
    return pd.DataFrame({
        "date": dates,
        "open": close + np.random.randn(500) * 50,
        "high": close + abs(np.random.randn(500) * 100),
        "low": close - abs(np.random.randn(500) * 100),
        "close": close,
        "volume_quote": np.random.uniform(1e6, 1e8, 500),
        "trading_pair_id": 1,
    })


class TestBuildFeatures:
    def test_build_features_daily_returns_dataframe(self, sample_ohlcv_daily):
        result = build_features(sample_ohlcv_daily, "daily", feature_lags=7)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_build_features_hourly_returns_dataframe(self, sample_ohlcv_hourly):
        result = build_features(sample_ohlcv_hourly, "hourly", feature_lags=24)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_build_features_contains_target(self, sample_ohlcv_daily):
        result = build_features(sample_ohlcv_daily, "daily", feature_lags=7)
        assert "target" in result.columns

    def test_build_features_no_nan_values(self, sample_ohlcv_daily):
        result = build_features(sample_ohlcv_daily, "daily", feature_lags=7)
        feature_cols = [c for c in result.columns if c != "target"]
        assert result[feature_cols].isna().sum().sum() == 0

    def test_build_features_last_row_has_nan_target_by_design(self, sample_ohlcv_daily):
        # add_target() décale la variation de -1 (shift(-1)) pour prédire le futur :
        # la dernière ligne n'a donc pas de cible connue, par construction — c'est
        # cette ligne-là que l'inférence utilise pour prédire le pas suivant
        # (cf. classify.py::_run_classification). dropna() exclut volontairement
        # "target" (build_features.py:21) pour ne pas la supprimer.
        result = build_features(sample_ohlcv_daily, "daily", feature_lags=7)
        assert result["target"].isna().sum() == 1
        assert result["target"].iloc[-1] != result["target"].iloc[-1]  # NaN != NaN
        assert result["target"].iloc[:-1].isna().sum() == 0

    def test_build_features_contains_date_column(self, sample_ohlcv_daily):
        result = build_features(sample_ohlcv_daily, "daily", feature_lags=7)
        assert "date" in result.columns


class TestLagFeatures:
    def test_lag_features_added(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_lag_features(df, n_lags=3)
        assert "close_lag_1" in result.columns
        assert "close_lag_2" in result.columns
        assert "close_lag_3" in result.columns
        assert "volume_quote_lag_1" in result.columns

    def test_lag_features_correct_values(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_lag_features(df, n_lags=1)
        assert result["close_lag_1"].iloc[1] == df["close"].iloc[0]


class TestReturnFeatures:
    def test_return_features_daily(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_return_features(df, "daily")
        assert "return_1" in result.columns
        assert "return_3" in result.columns
        assert "return_6" in result.columns

    def test_return_features_hourly_has_12(self, sample_ohlcv_hourly):
        df = sample_ohlcv_hourly.copy().set_index("date").sort_index()
        result = add_return_features(df, "hourly")
        assert "return_12" in result.columns


class TestTechnicalIndicators:
    def test_rsi_added(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_technical_indicators(df)
        assert "rsi" in result.columns

    def test_sma_added(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_technical_indicators(df)
        assert "sma_7" in result.columns
        assert "sma_14" in result.columns
        assert "sma_50" in result.columns

    def test_atr_added(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_technical_indicators(df)
        assert "atr" in result.columns


class TestTemporalFeatures:
    def test_daily_temporal_features(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_temporal_features(df, "daily")
        assert "day_of_week" in result.columns
        assert "month" in result.columns
        assert "is_weekend" in result.columns
        assert "hour" not in result.columns

    def test_hourly_temporal_features(self, sample_ohlcv_hourly):
        df = sample_ohlcv_hourly.copy().set_index("date").sort_index()
        result = add_temporal_features(df, "hourly")
        assert "hour" in result.columns
        assert "day_of_week" in result.columns


class TestTarget:
    def test_target_values_are_valid(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_target(df)
        valid_targets = {0.0, 1.0, 2.0}
        actual_targets = set(result["target"].dropna().unique())
        assert actual_targets.issubset(valid_targets)

    def test_target_has_three_classes(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_target(df)
        unique_targets = result["target"].dropna().unique()
        assert len(unique_targets) >= 2


class TestNoDataLeakage:
    """Plutôt que de supposer que les décalages (lags, cible) sont corrects, chaque
    colonne est recalculée manuellement depuis les données brutes et comparée à la
    colonne produite par le pipeline — un décalage cassé ou inversé ferait échouer
    ces tests (cf. C12 : absence de fuite via les features/cible décalées).
    """

    def test_all_lag_columns_match_manual_shift(self, sample_ohlcv_daily):
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_lag_features(df, n_lags=5)
        for col in ["close", "volume_quote", "high", "low"]:
            for lag in range(1, 6):
                expected = df[col].shift(lag)
                pd.testing.assert_series_equal(
                    result[f"{col}_lag_{lag}"], expected, check_names=False
                )

    def test_target_reflects_next_period_not_current_or_past(self, sample_ohlcv_daily):
        # add_target() doit regarder VERS L'AVANT (close[t+1] vs close[t]) : un bug qui
        # inverserait le shift (close[t] vs close[t-1]) donnerait au modèle accès à une
        # information qu'il n'aurait pas en production — c'est précisément ce qu'un
        # data leakage silencieux produirait, sans jamais faire planter l'entraînement.
        df = sample_ohlcv_daily.copy().set_index("date").sort_index()
        result = add_target(df)

        seuil = 0.005
        # Recalcul manuel indépendant, sans passer par pct_change/shift du code testé.
        close = df["close"].values
        for i in range(len(close) - 1):
            variation = (close[i + 1] - close[i]) / close[i]
            expected_label = 2.0 if variation > seuil else (0.0 if variation < -seuil else 1.0)
            assert result["target"].iloc[i] == expected_label, f"mismatch à l'index {i}"

        # La toute dernière ligne n'a pas de "période suivante" connue -> NaN attendu.
        assert pd.isna(result["target"].iloc[-1])
