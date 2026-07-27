"""Script de veille technologique — Fear & Greed Index via Alternative.me."""

import requests
import pandas as pd
from datetime import datetime


API_URL = "https://api.alternative.me/fng/"


def fetch_fear_and_greed(limit=30):
    """Récupère les `limit` dernières valeurs du Fear & Greed Index."""
    response = requests.get(API_URL, params={"limit": limit})
    if response.status_code != 200:
        raise RuntimeError(f"Échec requête ({response.status_code}): {response.text}")
    return response.json()["data"]


def build_dataframe(data):
    """Construit un DataFrame avec le score, la classification et la date."""
    df = pd.DataFrame(data)[["value", "value_classification", "timestamp"]]
    df.columns = ["score", "sentiment", "timestamp"]
    df["score"] = df["score"].astype(int)
    df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s").dt.strftime("%Y-%m-%d")
    return df[["date", "score", "sentiment"]].reset_index(drop=True)


def interpret_signal(score):
    """Retourne une interprétation simple du score."""
    if score <= 25:
        return "Vente excessive — opportunité d'achat potentielle"
    elif score <= 45:
        return "Peur — marché prudent"
    elif score <= 55:
        return "Neutre"
    elif score <= 75:
        return "Avidité — marché optimiste"
    else:
        return "Avidité extrême — risque de correction"


def main():
    print("=== Veille marché crypto — Fear & Greed Index (Alternative.me) ===\n")

    data = fetch_fear_and_greed(limit=30)
    df = build_dataframe(data)

    latest = df.iloc[0]
    print(f"Dernier signal ({latest['date']}) :")
    print(f"  Score     : {latest['score']} / 100")
    print(f"  Sentiment : {latest['sentiment']}")
    print(f"  Signal    : {interpret_signal(latest['score'])}")
    print()

    print("Historique des 30 derniers jours :")
    print(df.to_string(index=False))
    print()

    print("Distribution des sentiments sur 30 jours :")
    print(df["sentiment"].value_counts().to_string())


if __name__ == "__main__":
    main()
