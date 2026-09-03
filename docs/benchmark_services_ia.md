# Benchmark — Services d'IA pour la prédiction de tendance crypto

## 1. Expression de besoin

**Objectif :** Prédire la tendance du Bitcoin (hausse / baisse / stable) à court terme (24h) pour alimenter un outil d'aide à la décision destiné aux utilisateurs de la plateforme.

**Contraintes :**
- Données disponibles : cours OHLCV historiques + Fear & Greed Index
- Latence acceptable : < 5 secondes par prédiction
- Budget : limité (projet étudiant / certification)
- Reproductibilité : les prédictions doivent être cohérentes pour des données identiques
- Éco-responsabilité : minimiser l'empreinte carbone

---

## 2. Services étudiés

| Service | Type | Éditeur | Accès |
|---------|------|---------|-------|
| Anthropic Claude (Sonnet) | LLM généraliste | Anthropic | API cloud (crédits gratuits) |
| OpenAI GPT-4o | LLM généraliste | OpenAI | API cloud (payant) |
| Mistral Large | LLM généraliste | Mistral AI | API cloud (payant) |
| XGBoost (modèle custom Bloc3) | ML supervisé | Auto-hébergé | Local (Docker) |

---

## 3. Services non retenus et justification

### OpenAI GPT-4o
- **Raison d'exclusion :** Coût prohibitif pour un usage régulier (~0.01$/requête avec contexte long). Pas de crédits gratuits disponibles pour un projet étudiant.
- **Qualité estimée :** Comparable à Claude sur une tâche de raisonnement simple.

### Mistral Large
- **Raison d'exclusion :** Moins performant que Claude sur les tâches de raisonnement avec données tabulaires (benchmarks publics). Crédits gratuits limités.
- **Qualité estimée :** Légèrement inférieur aux deux autres LLM pour l'analyse de données structurées.

---

## 4. Comparaison détaillée — LLM (Claude) vs ML Custom (XGBoost)

| Critère | LLM (Anthropic Claude) | ML Custom (XGBoost Bloc3) |
|---------|----------------------|---------------------------|
| **Précision** | Faible — le LLM n'est pas entraîné sur des données financières récentes | Moyenne à bonne — entraîné spécifiquement sur les features OHLCV |
| **Reproductibilité** | Faible — réponses non déterministes, varient d'un appel à l'autre | Élevée — modèle déterministe à paramètres fixés |
| **Latence** | 2-5s (appel réseau + inférence cloud) | < 0.5s (inférence locale) |
| **Coût par requête** | ~0.003$ (input+output tokens) | 0$ (auto-hébergé, pas de coût marginal) |
| **Éco-responsabilité** | Forte empreinte — datacenter GPU pour chaque inférence | Faible empreinte — modèle léger, inférence CPU |
| **Données d'entraînement** | Corpus généraliste (coupure de connaissance) | Données OHLCV spécifiques au marché crypto, mises à jour |
| **Explicabilité** | Le LLM donne un raisonnement textuel (mais non vérifiable) | Feature importance quantifiable (SHAP, gain) |
| **Maintenance** | Aucune — service géré par Anthropic | Ré-entraînement périodique nécessaire (pipeline MLOps) |
| **Scalabilité** | Limitée par le rate-limit et le coût | Illimitée en local |

---

## 5. Adéquation par ensemble fonctionnel

| Fonction | LLM | ML Custom |
|----------|-----|-----------|
| Prédiction quantitative de tendance | ❌ Inadapté | ✅ Conçu pour |
| Analyse qualitative de marché | ✅ Pertinent | ❌ Non prévu |
| Synthèse d'actualités | ✅ Pertinent | ❌ Non prévu |
| Reproductibilité des résultats | ❌ Non garanti | ✅ Garanti |
| Explication du raisonnement | ⚠️ Textuel non vérifiable | ✅ Feature importance |

---

## 6. Démarche éco-responsable

Aucun des éditeurs comparés (Anthropic, OpenAI, Mistral) ne publie de chiffre officiel de consommation
énergétique ou d'empreinte carbone par requête d'inférence. Faute de pouvoir recouper un chiffre précis
avec au moins deux sources indépendantes fiables, aucune valeur n'est retenue ici comme mesurée.

Raisonnement qualitatif retenu : l'architecture privilégiant XGBoost local pour l'essentiel des
prédictions (inférence CPU de quelques millisecondes, ré-entraînement d'environ 5 min CPU par cycle)
sollicite structurellement moins de calcul distant qu'un appel LLM cloud à un modèle de fondation
multimodal hébergé en datacenter. C'est un argument de sobriété par conception, pas un résultat mesuré.

| Critère | LLM (Claude) | ML Custom |
|---------|-------------|-----------|
| Hébergement | Datacenter US (Anthropic) | Local / Docker auto-hébergé |
| Impact de l'entraînement | N/A (pré-entraîné) | Faible (~5min CPU pour XGBoost) |
| Chiffre officiel d'empreinte carbone | Non publié par l'éditeur | Non applicable (pas de service tiers) |

---

## 7. Contraintes techniques et pré-requis

### LLM (Anthropic Claude)
- Clé API Anthropic valide
- Connexion internet obligatoire
- Dépendance à un service tiers (disponibilité, pricing, changements d'API)
- Limite de rate (1000 req/min sur le tier gratuit)

### ML Custom (XGBoost Bloc3)
- Docker pour le déploiement
- Pipeline de données fonctionnel (API Bloc1 alimentant les OHLCV)
- Ré-entraînement périodique (cron configuré)
- Pas de dépendance externe à l'exécution

---

## 8. Conclusion

**Service retenu pour la prédiction de tendance : XGBoost (modèle custom Bloc3)**

Le modèle ML supervisé entraîné spécifiquement sur les données OHLCV du marché crypto est supérieur au LLM généraliste pour cette tâche :
- Il est **déterministe** et reproductible
- Il n'engendre **aucun coût** marginal par requête
- Son architecture locale sollicite structurellement **moins de calcul distant** qu'un appel LLM cloud (argument qualitatif, aucun chiffre officiel d'empreinte carbone disponible pour comparer)
- Il est **entraîné sur des données pertinentes** et récentes
- Il offre une **explicabilité** quantifiable (feature importance)

Le LLM (Anthropic Claude) reste pertinent comme **outil complémentaire** pour :
- La synthèse qualitative de conditions de marché
- L'explication textuelle des tendances à destination d'utilisateurs non techniques
- L'enrichissement de l'interface utilisateur (résumé en langage naturel)

Cette évaluation est implémentée et démontrable via l'application Streamlit (`Bloc2_veille/app_benchmark.py`), qui permet de lancer les deux services en parallèle et de comparer leurs résultats en temps réel.
