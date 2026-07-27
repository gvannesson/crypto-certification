"""Tests de l'évaluation du modèle de classification."""

import numpy as np
import pytest

from src.model.evaluate_model import compute_metrics


class TestComputeMetrics:
    def test_perfect_predictions(self):
        y_true = [0, 1, 2, 0, 1, 2]
        y_pred = [0, 1, 2, 0, 1, 2]
        metrics = compute_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 1.0
        assert metrics["f1_macro"] == 1.0
        assert metrics["f1_down"] == 1.0
        assert metrics["f1_stable"] == 1.0
        assert metrics["f1_up"] == 1.0

    def test_all_wrong_predictions(self):
        y_true = [0, 0, 0]
        y_pred = [2, 2, 2]
        metrics = compute_metrics(y_true, y_pred)

        assert metrics["accuracy"] == 0.0
        assert metrics["f1_down"] == 0.0

    def test_metrics_keys_present(self):
        y_true = [0, 1, 2, 1, 0]
        y_pred = [0, 1, 1, 2, 0]
        metrics = compute_metrics(y_true, y_pred)

        expected_keys = {"accuracy", "f1_macro", "f1_down", "f1_stable", "f1_up", "direction_accuracy"}
        assert set(metrics.keys()) == expected_keys

    def test_metrics_values_in_range(self):
        np.random.seed(42)
        y_true = np.random.choice([0, 1, 2], size=100).tolist()
        y_pred = np.random.choice([0, 1, 2], size=100).tolist()
        metrics = compute_metrics(y_true, y_pred)

        for key, value in metrics.items():
            assert 0.0 <= value <= 1.0, f"{key} hors limites : {value}"

    def test_direction_accuracy_ignores_stable_stable(self):
        y_true = [1, 1, 1, 1]
        y_pred = [1, 1, 1, 1]
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["direction_accuracy"] == 0.0

    def test_direction_accuracy_with_directional_predictions(self):
        y_true = [0, 2, 0, 2]
        y_pred = [0, 2, 0, 2]
        metrics = compute_metrics(y_true, y_pred)
        assert metrics["direction_accuracy"] == 1.0

    def test_empty_predictions_raises(self):
        with pytest.raises(ValueError):
            compute_metrics([], [])
