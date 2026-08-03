from django import forms


class ClassifyForm(forms.Form):
    PAIR_CHOICES = [("BTC-USDT", "BTC/USDT"), ("BTC-USD", "BTC/USD")]
    GRANULARITY_CHOICES = [("daily", "Journalier"), ("hourly", "Horaire")]

    trading_pair = forms.ChoiceField(
        choices=PAIR_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    granularity = forms.ChoiceField(
        choices=GRANULARITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
