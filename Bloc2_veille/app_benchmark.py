"""App Streamlit — POC appel LLM pour la prédiction de tendance BTC."""

import json
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import anthropic
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from parametrage import fetch_fear_and_greed, build_dataframe

load_dotenv()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
BLOC1_DIR = Path(__file__).parent.parent / "Bloc1_data"
SCRAPED_ARTICLES_PATH = BLOC1_DIR / "data" / "scraped_articles.json"

# Service ML (Bloc3, ml-api) — mêmes identifiants que ceux utilisés par le webapp Django (Bloc4).
ML_API_BASE_URL = os.getenv("API_E3_BASE_URL", "http://localhost:8002")
ML_API_USERNAME = os.getenv("API_E3_USERNAME", "")
ML_API_PASSWORD = os.getenv("API_E3_PASSWORD", "")

# Proxy LiteLLM (veille C6) — spend tracking par clé virtuelle, en complément de la console
# Anthropic. Si non configuré (LITELLM_VIRTUAL_KEY absente), l'app retombe sur l'appel direct
# à l'API Anthropic, sans que le POC ne soit bloqué.
LITELLM_PROXY_URL = os.getenv("LITELLM_PROXY_URL", "")
LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")
LITELLM_VIRTUAL_KEY = os.getenv("LITELLM_VIRTUAL_KEY", "")


def fetch_litellm_spend() -> dict:
    """Consommation/budget de la clé virtuelle LiteLLM utilisée par ce POC."""
    response = requests.get(
        f"{LITELLM_PROXY_URL}/key/info",
        params={"key": LITELLM_VIRTUAL_KEY},
        headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
        timeout=5,
    )
    response.raise_for_status()
    info = response.json()["info"]
    return {"spend": info["spend"], "max_budget": info["max_budget"], "alias": info["key_alias"]}


def fetch_xgboost_prediction(trading_pair_symbol: str = "BTC-USD") -> dict:
    """Interroge le service ml-api (XGBoost, Bloc3) pour comparer avec la prédiction LLM."""
    login_resp = requests.post(
        f"{ML_API_BASE_URL}/api/v1/authentification/login",
        data={"username": ML_API_USERNAME, "password": ML_API_PASSWORD},
        timeout=5,
    )
    login_resp.raise_for_status()
    token = login_resp.json()["access_token"]

    classify_resp = requests.post(
        f"{ML_API_BASE_URL}/api/v1/classify/classify_daily",
        json={"trading_pair_symbol": trading_pair_symbol},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    classify_resp.raise_for_status()
    predictions = classify_resp.json().get("predictions", [])
    return predictions[0] if predictions else {}

# Veille technique (C6) : suivi des annonces produit/modèle et, à défaut, des releases SDK.
# Deux natures de flux, documentées comme telles pour ne pas les confondre :
#   - flux RSS du blog éditeur (annonce modèle/produit réelle), quand l'éditeur en publie un ;
#   - à défaut de RSS public, flux Atom des releases GitHub du SDK, utilisé comme proxy imparfait
#     (une nouvelle release SDK accompagne souvent, mais pas toujours, un nouveau modèle).
VEILLE_SOURCES = [
    {
        "nom": "OpenAI (blog)",
        "type": "rss",
        "url": "https://openai.com/news/rss.xml",
        "nature": "Annonce modèle/produit (direct)",
    },
    {
        "nom": "Mistral AI (blog)",
        "type": "rss",
        "url": "https://mistral.ai/news/rss",
        "nature": "Annonce modèle/produit (direct)",
    },
    {
        "nom": "Anthropic SDK (GitHub)",
        "type": "github",
        "owner": "anthropics",
        "repo": "anthropic-sdk-python",
        "nature": "Proxy imparfait — Anthropic ne publie pas de flux RSS public",
    },
    {
        "nom": "XGBoost (GitHub)",
        "type": "github",
        "owner": "dmlc",
        "repo": "xgboost",
        "nature": "Release du modèle lui-même (direct)",
    },
]
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _fetch_github_release(owner: str, repo: str) -> dict:
    """Dernière entrée du flux Atom natif des releases GitHub (public, sans clé API)."""
    url = f"https://github.com/{owner}/{repo}/releases.atom"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    entry = root.find("atom:entry", ATOM_NS)
    return {
        "titre": entry.findtext("atom:title", default="", namespaces=ATOM_NS),
        "date": entry.findtext("atom:updated", default="", namespaces=ATOM_NS)[:10],
        "lien": entry.find("atom:link", ATOM_NS).attrib.get("href", ""),
    }


def _fetch_blog_rss(url: str) -> dict:
    """Dernière entrée d'un flux RSS 2.0 de blog éditeur."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    item = root.find(".//item")
    return {
        "titre": item.findtext("title", default=""),
        "date": item.findtext("pubDate", default="")[:16],
        "lien": item.findtext("link", default=""),
    }


def fetch_veille_signals() -> list[dict]:
    """Récupère le dernier signal (annonce blog ou release SDK) de chaque source suivie."""
    signals = []
    for source in VEILLE_SOURCES:
        try:
            if source["type"] == "github":
                latest = _fetch_github_release(source["owner"], source["repo"])
            else:
                latest = _fetch_blog_rss(source["url"])
        except (requests.RequestException, ET.ParseError) as exc:
            latest = {"titre": f"Indisponible ({exc})", "date": "", "lien": ""}
        signals.append({"source": source["nom"], "nature": source["nature"], **latest})
    return signals


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
    return df[["date", "price"]].sort_values("date", ascending=False).reset_index(drop=True)


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


def call_anthropic(prompt: str, api_key: str, temperature: float = 0.0) -> dict:
    """Appelle l'API Anthropic Claude et mesure la latence.

    Route via le proxy LiteLLM (passthrough Anthropic, spend tracking par clé virtuelle)
    quand il est configuré ; sinon appel direct à l'API Anthropic avec la clé fournie.
    """
    if LITELLM_PROXY_URL and LITELLM_VIRTUAL_KEY:
        client = anthropic.Anthropic(
            base_url=f"{LITELLM_PROXY_URL}/anthropic",
            api_key=LITELLM_VIRTUAL_KEY,
        )
    else:
        client = anthropic.Anthropic(api_key=api_key)

    start = time.time()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
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
        "model": ANTHROPIC_MODEL,
        "temperature": temperature,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def load_scraped_articles() -> list[dict]:
    """Charge les articles scrapés depuis le fichier JSON du Bloc1."""
    if not SCRAPED_ARTICLES_PATH.exists():
        return []
    with open(SCRAPED_ARTICLES_PATH) as f:
        return json.load(f)


def refresh_scraped_articles() -> tuple[bool, str]:
    """Lance le spider Scrapy du Bloc1 pour mettre à jour scraped_articles.json."""
    result = subprocess.run(
        ["uv", "run", "scrapy", "crawl", "cointelegraph"],
        cwd=BLOC1_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 0:
        return True, ""
    error = result.stderr.strip() or result.stdout.strip() or "Erreur inconnue"
    return False, error


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


def render_veille_tab():
    """Onglet C6 — veille technique : annonces modèles/produits + releases SDK."""
    st.header("Veille technique — annonces modèles et releases SDK")
    st.markdown(
        "Suivi des services d'IA comparés dans le benchmark (`docs/benchmark_services_ia.md`). "
        "Deux natures de flux, à ne pas confondre : le flux RSS du blog éditeur (annonce "
        "modèle/produit réelle), quand il existe, et à défaut le flux Atom des releases GitHub "
        "du SDK, utilisé comme proxy imparfait — une nouvelle release SDK accompagne souvent, "
        "mais pas toujours, un nouveau modèle."
    )
    with st.spinner("Récupération des derniers signaux..."):
        signals = fetch_veille_signals()
    df_signals = pd.DataFrame(signals)[["source", "nature", "titre", "date", "lien"]]
    st.dataframe(
        df_signals,
        width="stretch",
        hide_index=True,
        column_config={"lien": st.column_config.LinkColumn("Lien")},
    )
    st.caption(
        "OpenAI et Mistral publient un flux RSS de blog (signal direct sur les annonces "
        "modèle/produit). Anthropic ne publie aucun flux RSS public : le suivi des releases du "
        "SDK anthropic-sdk-python sert de proxy, documenté comme tel plutôt que présenté comme "
        "équivalent. XGBoost est suivi directement via ses releases GitHub, qui sont celles du "
        "modèle lui-même."
    )


def main():
    st.set_page_config(page_title="POC Prédiction BTC via LLM", page_icon="🔮", layout="wide")
    st.title("POC — Prédiction de tendance BTC via LLM")
    st.markdown(
        "Proof of concept : utilisation de l'API **Anthropic Claude** pour prédire la tendance "
        "du Bitcoin à court terme, à partir du Fear & Greed Index et du cours BTC sur 30 jours."
    )

    tab_poc, tab_veille = st.tabs(["POC Benchmark LLM", "Veille SDK (C6)"])

    with tab_veille:
        render_veille_tab()

    with tab_poc:
        _render_poc_tab()


def _render_poc_tab():
    if not ANTHROPIC_API_KEY:
        api_key = st.text_input("Clé API Anthropic", type="password")
    else:
        api_key = ANTHROPIC_API_KEY

    # --- Données ---
    st.header("1. Données d'entrée (30 derniers jours)")

    st.subheader("Actualités BTC (scraping CoinTelegraph)")
    st.caption(
        "Les articles proviennent d'un fichier statique (`Bloc1_data/data/scraped_articles.json`). "
        "Streamlit ne lance pas le scraping automatiquement : utilisez le bouton ci-dessous ou "
        "`cd Bloc1_data && uv run scrapy crawl cointelegraph`."
    )

    col_refresh, col_info = st.columns([1, 2])
    with col_refresh:
        if st.button("Rafraîchir les articles"):
            with st.spinner("Scraping CoinTelegraph en cours..."):
                ok, error = refresh_scraped_articles()
            if ok:
                st.success("Articles mis à jour.")
                st.rerun()
            else:
                st.error(f"Échec du scraping : {error}")

    articles = load_scraped_articles()
    if SCRAPED_ARTICLES_PATH.exists():
        updated_at = datetime.fromtimestamp(SCRAPED_ARTICLES_PATH.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M"
        )
        with col_info:
            st.caption(f"Dernière mise à jour du fichier : {updated_at}")

    if articles:
        df_articles = pd.DataFrame(articles)[["date", "category", "title"]]
        st.dataframe(df_articles, width="stretch", hide_index=True)
        st.caption(f"{len(articles)} articles — source : cointelegraph.com/tags/bitcoin")
    else:
        st.info("Aucun article disponible. Lancez le scraping pour alimenter les actualités.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Fear & Greed Index")
        with st.spinner("Chargement Fear & Greed..."):
            data = fetch_fear_and_greed(limit=30)
            df_sentiment = build_dataframe(data)
        st.dataframe(df_sentiment, width="stretch", height=300)

    with col2:
        st.subheader("Cours BTC (USD)")
        with st.spinner("Chargement cours BTC..."):
            df_prices = fetch_btc_prices_30d()
        st.dataframe(df_prices, width="stretch", height=300)

    # --- Prédiction ---
    st.divider()
    st.header("2. Prédiction LLM")

    if st.button("Lancer la prédiction", type="primary"):
        if not api_key:
            st.error("Veuillez renseigner votre clé API Anthropic.")
            return

        with st.spinner("Appel à l'API Anthropic Claude..."):
            prompt = build_llm_prompt(df_sentiment, df_prices)
            try:
                result = call_anthropic(prompt, api_key=api_key, temperature=0.0)
            except anthropic.APIError as exc:
                st.error(f"Erreur API Anthropic : {exc}")
                return

        st.subheader("Comparaison LLM vs ML (XGBoost, Bloc3)")
        col_llm, col_ml = st.columns(2)

        with col_llm:
            st.markdown("**LLM (Claude, zero-shot)**")
            st.metric("Prédiction", result["prediction"])
            if result["confidence"] != "N/A":
                st.caption(f"Confiance : {result['confidence']} — {result['reason']}")

        with col_ml:
            st.markdown("**ML (XGBoost, modèle entraîné)**")
            try:
                ml_result = fetch_xgboost_prediction("BTC-USD")
                if ml_result:
                    st.metric("Prédiction", ml_result["predicted_label"])
                    st.caption(
                        f"Confiance : {ml_result['confidence']:.0%} — "
                        f"pas de temps : {ml_result['date']}"
                    )
                else:
                    st.info("Aucune prédiction disponible (modèle pas encore entraîné pour cette paire).")
            except requests.RequestException as exc:
                st.warning(
                    f"Service ml-api indisponible ({exc}). Lancez "
                    "`docker compose up ml-api mlflow-server ml-pipeline -d` pour l'activer."
                )

        st.caption(
            "Le LLM répond à chaque appel sans garantie de reproductibilité ; le ML est déterministe "
            "et ses métriques de backtest (accuracy, f1_macro, direction_accuracy) sont trackées dans "
            "MLflow — cf. §3.7 du rapport pour le détail et la discussion de cette asymétrie."
        )

        with st.expander("Détails de l'appel LLM"):
            st.markdown(f"**Modèle :** `{result['model']}`")
            st.markdown(f"**Température :** `{result['temperature']}` (déterministe)")
            st.markdown(f"**Top-p :** non utilisé (redondant avec temperature=0)")
            st.markdown(f"**Max tokens :** `256`")
            st.markdown(f"**Tokens utilisés :** {result['input_tokens']} input + {result['output_tokens']} output")
            st.markdown(f"**Latence :** {result['latency_s']}s")
            if LITELLM_PROXY_URL and LITELLM_VIRTUAL_KEY:
                st.markdown(f"**Routage :** via proxy LiteLLM ({LITELLM_PROXY_URL})")
            else:
                st.markdown("**Routage :** appel direct API Anthropic (proxy LiteLLM non configuré)")

        if LITELLM_PROXY_URL and LITELLM_VIRTUAL_KEY:
            st.divider()
            st.subheader("Observabilité — veille C6 (LiteLLM)")
            st.caption(
                "Suivi des tokens/coût par clé API via le proxy LiteLLM (docs.litellm.ai), en "
                "complément de la console Anthropic — cf. §2.3 du rapport pour le déclencheur "
                "de cette veille et la comparaison avec un suivi manuel."
            )
            try:
                spend_info = fetch_litellm_spend()
                col_spend, col_budget = st.columns(2)
                col_spend.metric("Dépense cumulée (clé virtuelle)", f"${spend_info['spend']:.6f}")
                col_budget.metric("Budget max configuré", f"${spend_info['max_budget']:.2f}")
                st.caption(f"Clé virtuelle : `{spend_info['alias']}` — admin UI : {LITELLM_PROXY_URL}/ui")
            except requests.RequestException as exc:
                st.warning(f"Proxy LiteLLM indisponible ({exc}).")
        with st.expander("Réponse brute du LLM"):
            st.text(result["raw_response"])
        with st.expander("Prompt envoyé"):
            st.text(prompt)


if __name__ == "__main__":
    main()
