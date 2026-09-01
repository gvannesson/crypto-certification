"""Monitorage du modèle (C11) : dérive des prédictions stockées vs réalisé.

Réutilise les GET déjà exposés par Bloc1 (predictions_hourly/daily, ohlcv_hourly/daily),
indexés sur les mêmes clés (trading_pair_id, date) — aucune nouvelle table nécessaire.

Le seuil de classification (0,5 %) doit rester identique à celui utilisé pour entraîner
le modèle : cf. Bloc3_ml/config/ml_config.yaml (classification.seuil). Toute évolution de
ce seuil côté entraînement doit être répercutée ici pour que le réalisé recalculé reste
comparable à predicted_label.
"""

CLASSIFICATION_THRESHOLD = 0.005


def realized_label(prev_close, close):
    """Reproduit la règle de classification du pipeline d'entraînement (Bloc3_ml)."""
    if not prev_close:
        return None
    variation = (close - prev_close) / prev_close
    if variation > CLASSIFICATION_THRESHOLD:
        return "UP"
    if variation < -CLASSIFICATION_THRESHOLD:
        return "DOWN"
    return "STABLE"


def compute_drift_metrics(predictions, ohlcv):
    """Compare chaque prédiction stockée à l'issue réellement observée.

    predictions : liste de dicts {date, predicted_label, model_name, ...} (Bloc1 API)
    ohlcv       : liste de dicts {date, close, ...} (Bloc1 API, non nécessairement triée)

    Retourne (summary, rows) :
      summary : liste de {model_name, n, accuracy, accuracy_pct} — une entrée par modèle
      rows    : détail par prédiction évaluable {date, model_name, predicted, realized, correct}
    """
    close_by_date = {row["date"]: row["close"] for row in ohlcv}
    dates_sorted = sorted(close_by_date)
    prev_close_by_date = {
        dates_sorted[i]: close_by_date[dates_sorted[i - 1]] for i in range(1, len(dates_sorted))
    }

    per_model = {}
    rows = []
    for pred in predictions:
        close = close_by_date.get(pred["date"])
        prev_close = prev_close_by_date.get(pred["date"])
        if close is None or prev_close is None:
            continue  # réalisé pas encore connu (prédiction future ou OHLCV pas encore synchronisé)

        realized = realized_label(prev_close, close)
        model_name = pred.get("model_name") or "inconnu"
        is_correct = pred["predicted_label"] == realized
        # Même définition que Bloc3_ml/src/model/evaluate_model.py::compute_metrics :
        # exclut les cas où prédit ET réalisé valent tous les deux STABLE, pour ne pas
        # laisser une accuracy globale dominée par la classe majoritaire masquer la
        # capacité réelle du modèle à détecter une vraie hausse/baisse.
        counts_for_direction = not (pred["predicted_label"] == "STABLE" and realized == "STABLE")

        bucket = per_model.setdefault(model_name, {"correct": 0, "total": 0, "dir_correct": 0, "dir_total": 0})
        bucket["total"] += 1
        bucket["correct"] += int(is_correct)
        if counts_for_direction:
            bucket["dir_total"] += 1
            bucket["dir_correct"] += int(is_correct)

        rows.append({
            "date": pred["date"],
            "model_name": model_name,
            "predicted": pred["predicted_label"],
            "realized": realized,
            "correct": is_correct,
        })

    summary = []
    for model_name, bucket in sorted(per_model.items()):
        accuracy = bucket["correct"] / bucket["total"] if bucket["total"] else None
        direction_accuracy = bucket["dir_correct"] / bucket["dir_total"] if bucket["dir_total"] else None
        summary.append({
            "model_name": model_name,
            "n": bucket["total"],
            "accuracy": accuracy,
            "accuracy_pct": round(accuracy * 100, 1) if accuracy is not None else None,
            "direction_accuracy_pct": round(direction_accuracy * 100, 1) if direction_accuracy is not None else None,
        })

    rows.sort(key=lambda r: r["date"], reverse=True)
    return summary, rows
