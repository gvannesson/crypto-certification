"""App Streamlit — POC appel LLM pour la prédiction de tendance BTC."""

import json
import os
import time
from pathlib import Path

import anthropic
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from parametrage import fetch_fear_and_greed, build_dataframe

load_dotenv()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def fetch_btc_prices_30d() -> pd.DataFrame:
    """Récupère le cours BTC sur 30 jours via CoinGecko (API gratuite)."""
    response = requests.get(
        COINGECKO_URL,
        params={"vs_currency": "usd", "days": "30", "interval": "daily"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()["prices"]
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.strftime("%Y-%m-%d")
    df["price"] = df["price"].round(2)
    return df[["date", "price"]]


def build_llm_prompt(df_sentiment: pd.DataFrame, df_prices: pd.DataFrame) -> str:
    """Construit le prompt envoyé au LLM avec les données de marché."""
    merged = pd.merge(df_sentiment, df_prices, on="date", how="inner")
    table = merged.to_string(index=False)

    return f"""Tu es un analyste crypto. Voici les données des 30 derniers jours pour Bitcoin :
- Fear & Greed Index (score de 0 à 100, 0 = peur extrême, 100 = avidité extrême)
- Cours BTC en USD

{table}

En te basant uniquement sur ces données, prédis la tendance du Bitcoin pour les prochaines 24h.
Réponds STRICTEMENT au format suivant :
PREDICTION: [HAUSSE ou BAISSE ou STABLE]
CONFIANCE: [pourcentage entre 0 et 100]
RAISON: [une phrase courte expliquant ton raisonnement]"""


def call_anthropic(prompt: str, temperature: float = 0.0) -> dict:
    """Appelle l'API Anthropic Claude et mesure la latence."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=256,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.time() - start

    text = response.content[0].text
    prediction, confidence, reason = _parse_llm_response(text)

    return {
        "raw_response": text,
        "prediction": prediction,
        "confidence": confidence,
        "reason": reason,
        "latency_s": round(latency, 2),
        "model": "claude-sonnet-4-20250514",
        "temperature": temperature,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def _parse_llm_response(text: str) -> tuple[str, str, str]:
    """Parse la réponse du LLM pour extraire prédiction, confiance, raison."""
    prediction = "N/A"
    confidence = "N/A"
    reason = "N/A"

    for line in text.strip().split("\n"):
        upper = line.upper()
        if "PREDICTION" in upper:
            if "HAUSSE" in upper:
                prediction = "HAUSSE"
            elif "BAISSE" in upper:
                prediction = "BAISSE"
            else:
                prediction = "STABLE"
        elif "CONFIANCE" in upper:
            nums = "".join(c for c in line if c.isdigit())
            confidence = f"{nums}%" if nums else "N/A"
        elif "RAISON" in upper:
            reason = line.split(":", 1)[-1].strip() if ":" in line else line

    return prediction, confidence, reason


def main():
    st.set_page_config(page_title="POC Prédiction BTC via LLM", page_icon="🔮", layout="wide")
    st.title("POC — Prédiction de tendance BTC via LLM")
    st.markdown(
        "Proof of concept : utilisation de l'API **Anthropic Claude** pour prédire la tendance "
        "du Bitcoin à court terme, à partir du Fear & Greed Index et du cours BTC sur 30 jours."
    )

    if not ANTHROPIC_API_KEY:
        api_key = st.text_input("Clé API Anthropic", type="password")
    else:
        api_key = ANTHROPIC_API_KEY

    # --- Données ---
    st.header("1. Données d'entrée (30 derniers jours)")

    scraped_path = Path(__file__).parent.parent / "Bloc1_data" / "data" / "scraped_articles.json"
    if scraped_path.exists():
        with open(scraped_path) as f:
            articles = json.load(f)
        if articles:
            st.subheader("Actualités BTC récentes (scraping CoinTelegraph)")
            df_articles = pd.DataFrame(articles)[["date", "category", "title"]]
            st.dataframe(df_articles, use_container_width=True, hide_index=True)
            st.caption(f"{len(articles)} articles scrapés via Scrapy — source : cointelegraph.com/tags/bitcoin")
            st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fear & Greed Index")
        with st.spinner("Chargement Fear & Greed..."):
            data = fetch_fear_and_greed(limit=30)
            df_sentiment = build_dataframe(data)
        st.dataframe(df_sentiment, use_container_width=True, height=300)

    with col2:
        st.subheader("Cours BTC (USD)")
        with st.spinner("Chargement cours BTC..."):
            df_prices = fetch_btc_prices_30d()
        st.dataframe(df_prices, use_container_width=True, height=300)

    # --- Prédiction ---
    st.divider()
    st.header("2. Prédiction LLM")

    if st.button("Lancer la prédiction", type="primary"):
        if not api_key:
            st.error("Veuillez renseigner votre clé API Anthropic.")
            return

        os.environ["ANTHROPIC_API_KEY"] = api_key

        with st.spinner("Appel à l'API Anthropic Claude..."):
            prompt = build_llm_prompt(df_sentiment, df_prices)
            result = call_anthropic(prompt, temperature=0.0)

        st.metric("Prédiction", result["prediction"])

        with st.expander("Détails de l'appel"):
            st.markdown(f"**Modèle :** `{result['model']}`")
            st.markdown(f"**Température :** `{result['temperature']}` (déterministe)")
            st.markdown(f"**Top-p :** non utilisé (redondant avec temperature=0)")
            st.markdown(f"**Max tokens :** `256`")
            st.markdown(f"**Tokens utilisés :** {result['input_tokens']} input + {result['output_tokens']} output")
            st.markdown(f"**Latence :** {result['latency_s']}s")
        with st.expander("Réponse brute du LLM"):
            st.text(result["raw_response"])
        with st.expander("Prompt envoyé"):
            st.text(prompt)


if __name__ == "__main__":
    main()
