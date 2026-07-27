# Bloc2 — Veille Technologique & Benchmark IA

Veille marché crypto (Fear & Greed Index) et benchmark comparatif de services d'IA pour la prédiction de tendance.

## Contenu

| Fichier | Description |
|---------|-------------|
| `parametrage.py` | Script de veille — récupère et affiche le Fear & Greed Index (30 jours) |
| `app_benchmark.py` | App Streamlit — benchmark LLM (Anthropic Claude) vs modèle ML custom (Bloc3) |

## Installation

```bash
cd Bloc2_veille
uv sync
```

## Utilisation

### Veille — Fear & Greed Index
```bash
uv run python parametrage.py
```

Affiche :
- Dernier score et interprétation
- Historique 30 jours
- Distribution des sentiments

### Benchmark LLM vs ML Custom
```bash
# Nécessite une clé API Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
uv run streamlit run app_benchmark.py
```

L'application Streamlit permet de :
1. Visualiser les données d'entrée (Fear & Greed + cours BTC 30j)
2. Lancer une prédiction via LLM (Anthropic Claude)
3. Lancer une prédiction via le modèle ML custom (API Bloc3)
4. Comparer les résultats (latence, coût, reproductibilité, qualité)

## Dépendances

- `pandas` — Manipulation de données
- `requests` — Appels HTTP
- `anthropic` — SDK Anthropic pour l'appel au LLM
- `streamlit` — Interface web interactive
- `python-dotenv` — Gestion des variables d'environnement

## Documentation associée

- [Benchmark Services IA](../docs/benchmark_services_ia.md) — Document formel de benchmark (C7)
