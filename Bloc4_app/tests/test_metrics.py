"""Tests unitaires purs du calcul de dérive du modèle (dashboard/metrics.py, C11/C12).

Aucun accès réseau/DB : ces fonctions ne dépendent que de listes de dicts déjà
récupérées, donc entièrement testables sans mock.
"""

from dashboard.metrics import realized_label, compute_drift_metrics


class TestRealizedLabel:
    def test_up_when_variation_above_threshold(self):
        assert realized_label(100, 100.6) == "UP"

    def test_down_when_variation_below_threshold(self):
        assert realized_label(100, 99.4) == "DOWN"

    def test_stable_within_threshold(self):
        assert realized_label(100, 100.2) == "STABLE"

    def test_stable_at_exact_threshold_boundary(self):
        # variation == +0.5% pile : ni strictement > ni < seuil -> STABLE
        assert realized_label(100, 100.5) == "STABLE"

    def test_none_when_no_previous_close(self):
        assert realized_label(None, 100) is None

    def test_none_when_previous_close_is_zero(self):
        assert realized_label(0, 100) is None


class TestComputeDriftMetrics:
    def test_evaluates_only_predictions_with_known_realized(self):
        predictions = [
            {"date": "2026-01-02T00:00:00", "predicted_label": "UP", "model_name": "xgboost"},
            {"date": "2026-01-05T00:00:00", "predicted_label": "DOWN", "model_name": "xgboost"},
        ]
        ohlcv = [
            {"date": "2026-01-01T00:00:00", "close": 100},
            {"date": "2026-01-02T00:00:00", "close": 101},
            # pas de close pour 2026-01-04/05 -> la 2e prédiction n'est pas évaluable
        ]
        summary, rows = compute_drift_metrics(predictions, ohlcv)
        assert len(rows) == 1
        assert summary == [
            {"model_name": "xgboost", "n": 1, "accuracy": 1.0, "accuracy_pct": 100.0, "direction_accuracy_pct": 100.0}
        ]

    def test_accuracy_vs_direction_accuracy_diverge_on_stable_heavy_predictions(self):
        # Reproduit le cas réel observé en production : le modèle ne prédit que STABLE,
        # et le réalisé l'est aussi la plupart du temps -> accuracy haute, direction
        # accuracy basse car ces paires STABLE/STABLE n'y comptent pas.
        predictions = [
            {"date": f"2026-01-0{i}T00:00:00", "predicted_label": "STABLE", "model_name": "xgboost"}
            for i in range(2, 6)
        ]
        closes = [100, 100.05, 100.1, 100.05, 100.1]  # variations < 0,5% -> toutes STABLE
        ohlcv = [{"date": f"2026-01-0{i}T00:00:00", "close": c} for i, c in enumerate(closes, start=1)]

        summary, rows = compute_drift_metrics(predictions, ohlcv)
        assert summary[0]["accuracy_pct"] == 100.0
        assert summary[0]["direction_accuracy_pct"] is None  # aucune ligne ne compte pour la direction

    def test_empty_predictions_returns_empty_summary(self):
        summary, rows = compute_drift_metrics([], [{"date": "2026-01-01T00:00:00", "close": 100}])
        assert summary == []
        assert rows == []

    def test_groups_by_model_name(self):
        predictions = [
            {"date": "2026-01-02T00:00:00", "predicted_label": "UP", "model_name": "xgboost"},
            {"date": "2026-01-02T00:00:00", "predicted_label": "DOWN", "model_name": "ensemble"},
        ]
        ohlcv = [
            {"date": "2026-01-01T00:00:00", "close": 100},
            {"date": "2026-01-02T00:00:00", "close": 101},
        ]
        summary, rows = compute_drift_metrics(predictions, ohlcv)
        model_names = {row["model_name"] for row in summary}
        assert model_names == {"xgboost", "ensemble"}
