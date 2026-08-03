import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .services import DashboardService

PAIRS = [
    {"base": "BTC", "quote": "USDT", "label": "BTC/USDT"},
    {"base": "BTC", "quote": "USD", "label": "BTC/USD"},
]


@login_required
def dashboard_view(request):
    service = DashboardService()
    pair_data = []

    for pair in PAIRS:
        tp = service.get_trading_pair(pair["base"], pair["quote"])
        if not tp:
            continue

        predictions = service.get_predictions(tp["id"], "daily")
        last_pred = predictions[-1] if predictions else None
        if last_pred and "confidence" in last_pred:
            last_pred["confidence_pct"] = last_pred["confidence"] * 100

        ohlcv = service.get_ohlcv(tp["id"], "daily")
        last_price = ohlcv[-1]["close"] if ohlcv else None

        pair_data.append({
            "label": pair["label"],
            "last_price": last_price,
            "last_prediction": last_pred,
        })

    return render(request, "dashboard/index.html", {"pairs": pair_data})


@login_required
def charts_view(request):
    return render(request, "dashboard/charts.html", {"pairs": PAIRS})


@login_required
def api_chart_data(request):
    """API interne JSON pour les graphiques — appelée en AJAX depuis charts.html."""
    base = request.GET.get("base", "BTC")
    quote = request.GET.get("quote", "USDT")
    granularity = request.GET.get("granularity", "daily")

    service = DashboardService()
    tp = service.get_trading_pair(base, quote)
    if not tp:
        return JsonResponse({"error": "Paire introuvable"}, status=404)

    ohlcv = service.get_ohlcv(tp["id"], granularity)
    predictions = service.get_predictions(tp["id"], granularity)

    return JsonResponse({"ohlcv": ohlcv, "predictions": predictions})
