from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ClassifyForm
from .services import ForecastService


@login_required
def classify_view(request):
    form = ClassifyForm()
    prediction = None

    if request.method == "POST":
        form = ClassifyForm(request.POST)
        if form.is_valid():
            service = ForecastService()
            try:
                result = service.get_classification(
                    trading_pair_symbol=form.cleaned_data["trading_pair"],
                    granularity=form.cleaned_data["granularity"],
                )
                if "error" in result:
                    messages.error(request, result["error"])
                else:
                    preds = result.get("predictions", [])
                    if preds:
                        prediction = preds[0]
                        prediction["confidence_pct"] = prediction.get("confidence", 0) * 100
            except Exception as e:
                messages.error(request, f"Erreur de connexion à l'API ML : {e}")

    return render(request, "forecast/classify.html", {"form": form, "prediction": prediction})
