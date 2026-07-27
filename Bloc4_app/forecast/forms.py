from django import forms


class ClassifyForm(forms.Form):
    PAIR_CHOICES = [("BTC-USDT", "BTC/USDT"), ("BTC-USD", "BTC/USD")]
    GRANULARITY_CHOICES = [("hourly", "Horaire"), ("daily", "Journalier")]
    NUM_PRED_CHOICES = [(i, str(i)) for i in range(1, 25)]

    trading_pair = forms.ChoiceField(
        choices=PAIR_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    granularity = forms.ChoiceField(
        choices=GRANULARITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    num_pred = forms.ChoiceField(
        choices=NUM_PRED_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Nombre de prédictions",
    )
