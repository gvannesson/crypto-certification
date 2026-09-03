# Référentiel de Compétences — Développeur en Intelligence Artificielle

## Bloc 1 : Réaliser la collecte, le stockage et la mise à disposition des données d'un projet en IA

### C1 — Automatiser l'extraction de données depuis plusieurs sources

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Présentation du projet et contexte complète | ✅ |
| 2 | Spécifications techniques (technologies, outils, langages, accessibilité) | ✅ |
| 3 | Périmètre des spécifications couvre l'ensemble des moyens techniques | ✅ |
| 4 | Script d'extraction fonctionnel | ✅ |
| 5 | Script comprend point de lancement, dépendances, gestion erreurs, sauvegarde | ✅ |
| 6 | Script versionné et accessible depuis un dépôt Git | ✅ |
| 7 | Extraction depuis un mix de sources (API REST, fichier, scraping, BDD, big data) | ✅ API REST (Binance, CoinMarketCap, Alternative.me) + fichiers CSV + Scraping Scrapy (CoinTelegraph) + BDD PostgreSQL |

### C2 — Développer des requêtes SQL d'extraction

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Requêtes SQL fonctionnelles | ✅ |
| 2 | Documentation des choix de sélections, filtrages, jointures | ✅ Documenté dans `Bloc1_data/README.md` |
| 3 | Documentation des optimisations appliquées aux requêtes | ✅ Documenté dans `Bloc1_data/README.md` (joinedload, batch insert, contraintes) |

### C3 — Développer des règles d'agrégation de données

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Script d'agrégation fonctionnel (données agrégées, nettoyées, normalisées) | ✅ |
| 2 | Script versionné sur Git | ✅ |
| 3 | Documentation complète (dépendances, commandes, algorithme, choix de nettoyage) | ✅ Documenté dans `Bloc1_data/README.md` (algorithme d'agrégation OHLCV) |

### C4 — Créer une base de données dans le respect du RGPD

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Modélisation respecte le formalisme Merise | ✅ MCD Merise dans `docs/specifications_fonctionnelles.md` |
| 2 | Modèle physique fonctionnel (intégré sans erreur) | ✅ |
| 3 | Base de données choisie au regard des contraintes | ✅ PostgreSQL |
| 4 | Procédures d'installation reproductibles (Docker) | ✅ |
| 5 | Script d'import fonctionnel | ✅ |
| 6 | Documentation technique versionnée | ✅ `Bloc1_data/README.md` |
| 7 | Documentation couvre dépendances + commandes d'exécution | ✅ `Bloc1_data/README.md` |
| 8 | Registre des traitements de données personnelles (RGPD) | ✅ `docs/rgpd_registre_traitements.md` |
| 9 | Procédures de tri des données personnelles rédigées | ✅ `docs/rgpd_registre_traitements.md` (section 3) |
| 10 | Procédures détaillent les traitements de conformité et leur fréquence | ✅ `docs/rgpd_registre_traitements.md` (section 3.6) |

### C5 — Développer une API REST mettant à disposition le jeu de données

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Documentation technique couvre tous les endpoints | ✅ Auto-générée via OpenAPI /docs |
| 2 | Documentation couvre les règles d'authentification | ✅ JWT documenté dans OpenAPI |
| 3 | Documentation respecte les standards (OpenAPI) | ✅ |
| 4 | API fonctionnelle avec authentification | ✅ |
| 5 | API permet la récupération de l'ensemble des données | ✅ |

---

## Bloc 2 : Intégrer des modèles et des services d'intelligence artificielle

### C6 — Organiser et réaliser une veille technique et réglementaire

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Thématique de veille porte sur un outil/réglementation du projet | ✅ Fear & Greed Index |
| 2 | Temps de veille planifiés régulièrement (min. 1h/semaine) | ✅ Documenté dans `docs/methodologie_agile.md` (rituels) |
| 3 | Outils d'agrégation cohérents avec les sources | ✅ API Alternative.me + App Streamlit |
| 4 | Synthèses accessibles (WCAG, Valentin Haüy, AcceDe) | ⚠️ Partiel — App Streamlit accessible |
| 5 | Informations partagées répondent à la thématique | ✅ |
| 6 | Sources fiables (auteur identifié, compétences, absence d'intérêts) | ✅ |

### C7 — Identifier des services d'IA préexistants (benchmark)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Expression de besoin reformulée avec objectifs et contraintes | ✅ `docs/benchmark_services_ia.md` section 1 |
| 2 | Benchmark liste les services étudiés et non étudiés | ✅ Section 2 (4 services étudiés) |
| 3 | Raisons pour écarter un service explicitées | ✅ Section 3 (OpenAI, Mistral écartés) |
| 4 | Niveau d'adéquation détaillé par ensemble fonctionnel | ✅ Section 5 (tableau par fonction) |
| 5 | Niveau de démarche éco-responsable détaillé | ✅ Section 6 (consommation, CO2, hébergement) |
| 6 | Contraintes techniques et pré-requis détaillés | ✅ Section 7 |
| 7 | Conclusions claires (services retenus vs écartés) | ✅ Section 8 (ML custom retenu, LLM complémentaire) |

> **✅ Compétence réalisée — `docs/benchmark_services_ia.md` + `Bloc2_veille/app_benchmark.py` (Streamlit)**

### C8 — Paramétrer un service d'IA

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Service installé et accessible (avec authentification) | ✅ MLflow accessible port 5000 |
| 2 | Service configuré, répond aux besoins fonctionnels | ✅ |
| 3 | Monitorage du service opérationnel | ✅ MLflow UI |
| 4 | Documentation (accès, installation, dépendances, données) | ✅ `Bloc3_ml/README.md` |
| 5 | Documentation accessible (WCAG) | ⚠️ Partiel |

### C9 — Développer une API exposant un modèle d'IA

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | API restreint l'accès avec authentification | ✅ JWT |
| 2 | API permet l'accès aux fonctions du modèle | ✅ classify_hourly, classify_daily |
| 3 | Recommandations OWASP intégrées | ✅ Documenté dans `Bloc4_app/README.md` (tableau OWASP) |
| 4 | Sources versionnées sur Git distant | ✅ |
| 5 | Tests couvrent tous les endpoints | ✅ tests/test_api_classify.py |
| 6 | Tests s'exécutent sans bug | ✅ 36 tests passent |
| 7 | Résultats des tests correctement interprétés | ✅ |
| 8 | Documentation couvre l'architecture et les endpoints | ✅ OpenAPI /docs + `Bloc3_ml/README.md` |
| 9 | Documentation couvre les règles d'auth | ✅ |
| 10 | Documentation respecte un standard (OpenAPI) | ✅ |
| 11 | Documentation accessible | ⚠️ Partiel |

### C10 — Intégrer l'API d'un modèle dans une application

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Application installée et fonctionnelle | ✅ Django + Docker |
| 2 | Communication avec l'API fonctionne | ✅ services.py appelle les APIs |
| 3 | Authentification et renouvellement intégrés | ✅ JWT géré |
| 4 | Tous les endpoints concernés intégrés | ✅ |
| 5 | Interfaces adaptées selon spécifications | ✅ Dashboard, Charts, Classify |
| 6 | Tests d'intégration couvrent les endpoints exploités | ✅ tests/test_services.py + test_dashboard.py |
| 7 | Tests s'exécutent sans bug | ✅ 38 tests passent |
| 8 | Résultats des tests interprétés | ✅ |
| 9 | Sources versionnées sur Git | ✅ |

### C11 — Monitorer un modèle d'IA

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Métriques expliquées sans erreur d'interprétation | ✅ accuracy, F1, direction_accuracy |
| 2 | Outils adaptés au contexte technique | ✅ MLflow |
| 3 | Restitution des métriques en temps réel (dashboard) | ✅ MLflow UI port 5000 |
| 4 | Enjeux d'accessibilité pris en compte | ⚠️ Partiel |
| 5 | Chaîne testée en environnement de test | ⚠️ Partiel — CI GitHub Actions |
| 6 | Chaîne en état de marche | ✅ monitor_training.py exécuté par cron |
| 7 | Sources versionnées sur Git | ✅ |
| 8 | Documentation technique de la chaîne | ✅ `Bloc3_ml/README.md` (section MLOps) |
| 9 | Documentation accessible | ⚠️ Partiel |

### C12 — Programmer les tests automatisés d'un modèle d'IA

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Cas à tester listés et définis | ✅ test_build_features.py + test_evaluate_model.py |
| 2 | Outils de test cohérents (pytest) | ✅ |
| 3 | Tests intégrés avec couverture | ✅ 52% couverture Bloc3 |
| 4 | Tests s'exécutent sans problème technique | ✅ 36 tests passent |
| 5 | Sources versionnées sur Git | ✅ |
| 6 | Documentation (installation, exécution, couverture) | ✅ `Bloc3_ml/README.md` (section Tests) |
| 7 | Documentation accessible | ⚠️ Partiel |

### C13 — Créer une chaîne de livraison continue (MLOps)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Documentation couvre étapes, tâches et déclencheurs | ✅ `Bloc3_ml/README.md` (section Chaîne MLOps) |
| 2 | Déclencheurs intégrés | ✅ Cron horaire + journalier |
| 3 | Fichiers de configuration reconnus et exécutés | ✅ entrypoint.sh + CI GitHub Actions |
| 4 | Étape de test des données intégrée | ⚠️ Partiel — validation dans build_features |
| 5 | Étapes de test, entraînement et validation intégrées | ✅ Pipeline complet (fetch → features → train → evaluate → save) |
| 6 | Sources versionnées sur Git | ✅ |
| 7 | Documentation de la chaîne (installation, configuration, test) | ✅ `Bloc3_ml/README.md` |
| 8 | Documentation accessible | ⚠️ Partiel |

---

## Bloc 3 : Réaliser une application intégrant un service d'intelligence artificielle

### C14 — Analyser le besoin (spécifications fonctionnelles)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Modélisation des données respecte un formalisme (Merise, ER) | ✅ MCD Merise dans `docs/specifications_fonctionnelles.md` |
| 2 | Modélisation des parcours utilisateurs (wireframes, schéma fonctionnel) | ✅ Wireframes + parcours (sections 3-4) |
| 3 | Spécifications fonctionnelles (contexte, scénarios, critères de validation) | ✅ Scénarios d'acceptation (section 5) |
| 4 | Objectifs d'accessibilité intégrés aux critères d'acceptation | ✅ Section 6 (WCAG 2.1 AA) |
| 5 | Objectifs d'accessibilité basés sur un standard (WCAG, RGAA) | ✅ WCAG 2.1 AA |

> **✅ Compétence réalisée — `docs/specifications_fonctionnelles.md`**

### C15 — Concevoir le cadre technique (architecture)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Spécifications techniques (architecture, dépendances, environnement) | ✅ `docs/architecture.md` |
| 2 | Services éco-responsables favorisés | ✅ Documenté (images Docker légères, modèles légers, monitoring éco) |
| 3 | Diagramme de flux de données | ✅ `docs/architecture.md` (section 3 — Flux de données) |
| 4 | Preuve de concept accessible et fonctionnelle | ✅ Docker compose fonctionnel |
| 5 | Conclusion permettant prise de décision | ✅ Tableau justification technos (section 4) |

### C16 — Coordonner la réalisation (méthode agile)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Cycles, étapes, rôles, rituels respectés | ✅ `docs/methodologie_agile.md` (section 2) |
| 2 | Outils de pilotage disponibles (kanban, backlog) | ✅ GitHub Projects — board Kanban actif |
| 3 | Objectifs et modalités partagés | ✅ Issues avec critères d'acceptation |
| 4 | Éléments de pilotage accessibles tout au long du projet | ✅ Board public sur GitHub |

> **✅ Compétence réalisée — GitHub Projects + `docs/methodologie_agile.md`**

### C17 — Développer les composants et interfaces

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Environnement de développement conforme | ✅ Docker + pyproject.toml |
| 2 | Interfaces intégrées respectent les maquettes | ✅ Bootstrap, templates Django |
| 3 | Comportements composants (formulaires, navigation) fonctionnels | ✅ |
| 4 | Composants métier développés selon spécifications | ✅ Dashboard, Forecast, Accounts |
| 5 | Gestion des droits d'accès | ✅ @login_required |
| 6 | Flux de données intégrés | ✅ |
| 7 | Bonnes pratiques éco-conception | ✅ Documenté dans `docs/architecture.md` |
| 8 | Top 10 OWASP implémenté | ✅ Documenté dans `Bloc4_app/README.md` (tableau OWASP) |
| 9 | Tests d'intégration/unitaires (composants métier + accès) | ✅ 38 tests Django |
| 10 | Sources versionnées sur Git | ✅ |
| 11 | Documentation technique (installation, architecture, tests) | ✅ `Bloc4_app/README.md` |
| 12 | Documentation accessible | ⚠️ Partiel |

### C18 — Automatiser les tests (intégration continue)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Documentation couvre outils, étapes, déclencheurs | ✅ `Bloc4_app/README.md` (section CI) |
| 2 | Outil CI sélectionné (cohérent avec l'environnement) | ✅ GitHub Actions |
| 3 | Chaîne intègre les étapes préalables aux tests | ✅ install deps + pytest |
| 4 | Chaîne exécute les tests lors du déclenchement | ✅ on push/PR |
| 5 | Configurations versionnées sur Git | ✅ .github/workflows/ci.yml |
| 6 | Documentation CI (installation, configuration, test) | ✅ `Bloc4_app/README.md` |
| 7 | Documentation accessible | ⚠️ Partiel |

### C19 — Créer un processus de livraison continue

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Documentation couvre étapes, tâches, déclencheurs | ✅ `Bloc4_app/README.md` (section CD) |
| 2 | Fichiers de configuration reconnus et exécutés | ✅ docker-compose + Dockerfiles |
| 3 | Étapes de packaging (build containers) intégrées | ✅ Dockerfiles fonctionnels |
| 4 | Étape de livraison (PR) intégrée | ✅ Workflow PR → CI → merge → deploy |
| 5 | Sources versionnées sur Git | ✅ |
| 6 | Documentation de la chaîne | ✅ `Bloc4_app/README.md` |
| 7 | Documentation accessible | ⚠️ Partiel |

### C20 — Surveiller une application (monitoring applicatif)

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Documentation des métriques et seuils d'alerte | ✅ `docs/monitoring_applicatif.md` (sections 2-3) |
| 2 | Arguments en faveur des choix techniques documentés | ✅ Section 6 (justification Prometheus/Grafana) |
| 3 | Outils installés et opérationnels (collecteurs, dashboard) | ✅ Prometheus + Grafana dans docker-compose |
| 4 | Règles de journalisation intégrées aux sources | ✅ logging Python + métriques Prometheus |
| 5 | Alertes configurées et en état de marche | ✅ 3 alertes (HighErrorRate, HighLatency, ServiceDown) |
| 6 | Documentation (installation, configuration) | ✅ `docs/monitoring_applicatif.md` |
| 7 | Documentation accessible | ⚠️ Partiel |

> **✅ Compétence réalisée — Prometheus + Grafana + `docs/monitoring_applicatif.md`**

### C21 — Résoudre les incidents techniques

| # | Critère d'évaluation | Statut |
|---|----------------------|--------|
| 1 | Causes du problème identifiées correctement | ✅ `docs/resolution_incident.md` (section 4) |
| 2 | Problème reproduit en environnement de développement | ✅ Étapes de reproduction documentées (section 3) |
| 3 | Procédure de débogage documentée (outil de suivi) | ✅ Issue GitHub #4 |
| 4 | Solution documentée (chaque étape) | ✅ Section 5 (code + explication) |
| 5 | Solution versionnée sur Git (merge request) | ✅ Fix dans `Bloc1_data/src/C5_api/routes/ohlcv.py` |

> **✅ Compétence réalisée — `docs/resolution_incident.md` + Issue #4 + fix versionné**

---

## Synthèse globale

| Compétence | Statut | Priorité restante |
|-----------|--------|-------------------|
| C1 | ✅ Complété | — |
| C2 | ✅ Complété | — |
| C3 | ✅ Complété | — |
| C4 | ✅ Complété | — |
| C5 | ✅ Complété | — |
| C6 | ⚠️ Partiel | Accessibilité |
| C7 | ✅ Complété | — |
| C8 | ✅ Complété | — |
| C9 | ✅ Complété | — |
| C10 | ✅ Complété | — |
| C11 | ⚠️ Partiel | Accessibilité |
| C12 | ✅ Complété | — |
| C13 | ⚠️ Partiel | Test data dans pipeline |
| C14 | ✅ Complété | — |
| C15 | ✅ Complété | — |
| C16 | ✅ Complété | — |
| C17 | ✅ Complété | — |
| C18 | ✅ Complété | — |
| C19 | ✅ Complété | — |
| C20 | ✅ Complété | — |
| C21 | ✅ Complété | — |

### Comptage

- ✅ **Complétées** : C1, C2, C3, C4, C5, C7, C8, C9, C10, C12, C14, C15, C16, C17, C18, C19, C20, C21 → **18/21**
- ⚠️ **Partielles** : C6, C11, C13 → **3/21**
- ❌ **Absentes** : aucune → **0/21**

### Actions restantes (optionnelles)

1. **Scraping C1** — Ajouter une source de données par scraping web (Issue #8)
2. **Accessibilité C6/C11** — Audit WCAG de l'app Django et des docs (Issue #9)
3. **Test data C13** — Ajouter une étape de validation des données dans le pipeline ML
