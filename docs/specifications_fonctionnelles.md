# Spécifications Fonctionnelles — Plateforme de Classification de Tendance Crypto

## 1. Contexte du projet

La plateforme "Crypto Certification" est un outil d'aide à la décision pour le marché des cryptomonnaies. Elle collecte des données de marché (OHLCV), entraîne des modèles de machine learning pour classifier la tendance (UP / STABLE / DOWN), et expose les résultats via une application web.

**Public cible :** Investisseurs crypto souhaitant une vision synthétique et des prédictions à court terme.

---

## 2. Modélisation des données (MCD — Modèle Conceptuel de Données)

### Entités et attributs

```
CURRENCY (#id, name, symbol, slug, sign, rank, rank_date, type)
EXCHANGE (#id, name, slug)
TRADING_PAIR (#id, base_currency_id, quote_currency_id)
CRYPTOCURRENCY_CSV (#id, exchange_id, trading_pair_id, timeframe, start_date, end_date, file_url)
CSV_HISTORICAL_DATA (#id, csv_file_id, date, open, high, low, close, volume_quote)
OHLCV_MINUTE (#id, trading_pair_id, date, open, high, low, close, volume_quote)
OHLCV_HOURLY (#id, trading_pair_id, date, open, high, low, close, volume_quote)
OHLCV_DAILY (#id, trading_pair_id, date, open, high, low, close, volume_quote)
PREDICTION_HOURLY (#id, trading_pair_id, date, predicted_class, predicted_label, confidence, model_name)
PREDICTION_DAILY (#id, trading_pair_id, date, predicted_class, predicted_label, confidence, model_name)
USER (#id, username, password_hashed, status, role)
```

### Relations (cardinalités)

```
CURRENCY (1,n) --- possède --- (0,n) TRADING_PAIR [base_currency]
CURRENCY (1,n) --- possède --- (0,n) TRADING_PAIR [quote_currency]
TRADING_PAIR (1,1) --- génère --- (0,n) OHLCV_MINUTE
TRADING_PAIR (1,1) --- génère --- (0,n) OHLCV_HOURLY
TRADING_PAIR (1,1) --- génère --- (0,n) OHLCV_DAILY
TRADING_PAIR (1,1) --- reçoit --- (0,n) PREDICTION_HOURLY
TRADING_PAIR (1,1) --- reçoit --- (0,n) PREDICTION_DAILY
TRADING_PAIR (1,1) --- référencé_par --- (0,n) CRYPTOCURRENCY_CSV
EXCHANGE (1,1) --- fournit --- (0,n) CRYPTOCURRENCY_CSV
CRYPTOCURRENCY_CSV (1,1) --- contient --- (0,n) CSV_HISTORICAL_DATA
```

### Diagramme MCD (notation Merise)

```
┌─────────────┐          ┌──────────────┐          ┌─────────────┐
│  CURRENCY   │──(1,n)──<  est_base_de  >──(0,n)──│TRADING_PAIR │
│             │          └──────────────┘          │             │
│  #id        │          ┌──────────────┐          │  #id        │
│  name       │──(1,n)──<  est_quote_de >──(0,n)──│  base_curr  │
│  symbol     │          └──────────────┘          │  quote_curr │
│  type       │                                    └──────┬──────┘
└─────────────┘                                           │
                                                    (1,1) │
                          ┌───────────────────────────────┼───────────────────┐
                          │                               │                   │
                    (0,n) ▼                         (0,n) ▼             (0,n) ▼
              ┌───────────────┐                ┌──────────────┐   ┌────────────────┐
              │  OHLCV_DAILY  │                │ OHLCV_HOURLY │   │ PREDICTION_*   │
              │  date, OHLCV  │                │ date, OHLCV  │   │ date, class    │
              └───────────────┘                └──────────────┘   │ label, conf.   │
                                                                  └────────────────┘
```

---

## 3. Parcours utilisateurs

### 3.1 Inscription / Connexion

| Étape | Action utilisateur | Réponse système |
|-------|-------------------|-----------------|
| 1 | Accède à `/accounts/register/` | Affiche formulaire d'inscription |
| 2 | Remplit username + mot de passe (x2) | Valide le formulaire |
| 3 | Soumet | Crée le compte, connecte, redirige vers `/dashboard/` |
| Alt | Identifiants invalides | Message d'erreur, reste sur le formulaire |

### 3.2 Dashboard principal

| Étape | Action utilisateur | Réponse système |
|-------|-------------------|-----------------|
| 1 | Accède à `/dashboard/` (authentifié) | Affiche les paires (BTC/USDT, BTC/USD) |
| 2 | Visualise le dernier prix et la dernière prédiction | Données récupérées depuis l'API Bloc1 |

### 3.3 Graphiques interactifs

| Étape | Action utilisateur | Réponse système |
|-------|-------------------|-----------------|
| 1 | Accède à `/dashboard/charts/` | Affiche la page avec sélecteurs |
| 2 | Sélectionne une paire et une granularité | Charge les données OHLCV + prédictions en AJAX |
| 3 | Explore le graphique | Interactif (zoom, tooltip) |

### 3.4 Classification à la demande (Forecast)

| Étape | Action utilisateur | Réponse système |
|-------|-------------------|-----------------|
| 1 | Accède à `/forecast/classify/` | Affiche le formulaire |
| 2 | Choisit : paire, granularité (daily/hourly), nombre de prédictions | Valide les choix |
| 3 | Soumet | Appelle l'API ML Bloc3 `/classify/classify_daily` ou `_hourly` |
| 4 | Visualise les résultats | Affiche : date, classe prédite, label, confiance |
| Alt | API indisponible | Message d'erreur explicite |

---

## 4. Wireframes (description structurelle)

### Page Login (`/accounts/login/`)
```
┌─────────────────────────────────────┐
│           CRYPTO APP                │
├─────────────────────────────────────┤
│                                     │
│   ┌──────────────────────────┐      │
│   │ Username: [____________] │      │
│   │ Password: [____________] │      │
│   │                          │      │
│   │      [Se connecter]      │      │
│   │                          │      │
│   │  Pas de compte ? S'inscrire     │
│   └──────────────────────────┘      │
│                                     │
└─────────────────────────────────────┘
```

### Page Dashboard (`/dashboard/`)
```
┌─────────────────────────────────────┐
│  NAV: Dashboard | Charts | Forecast │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │ BTC/USDT │  │ BTC/USD  │        │
│  │ $97,234  │  │ $97,234  │        │
│  │ ↑ UP 78% │  │ → STABLE │        │
│  └──────────┘  └──────────┘        │
│                                     │
└─────────────────────────────────────┘
```

### Page Classify (`/forecast/classify/`)
```
┌─────────────────────────────────────┐
│  NAV: Dashboard | Charts | Forecast │
├─────────────────────────────────────┤
│                                     │
│  Paire:       [BTCUSDT     ▼]      │
│  Granularité: [daily       ▼]      │
│  Prédictions: [3           ▼]      │
│                                     │
│  [Lancer la classification]         │
│                                     │
│  ┌─────────┬────────┬──────────┐   │
│  │ Date    │ Classe │ Confiance│   │
│  ├─────────┼────────┼──────────┤   │
│  │ 07/05   │ UP     │ 72.3%   │   │
│  │ 08/05   │ STABLE │ 55.1%   │   │
│  │ 09/05   │ DOWN   │ 61.8%   │   │
│  └─────────┴────────┴──────────┘   │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Scénarios d'acceptation (critères de validation)

### SC-01 : Inscription utilisateur
- **Pré-condition :** L'utilisateur n'a pas de compte
- **Scénario :** Remplit formulaire avec username unique et mot de passe conforme
- **Post-condition :** Compte créé, utilisateur connecté, redirigé vers dashboard
- **Critère :** Mot de passe hashé en base (jamais en clair)

### SC-02 : Consultation du dashboard
- **Pré-condition :** Utilisateur connecté
- **Scénario :** Accède à `/dashboard/`
- **Post-condition :** Voit le dernier prix et la dernière prédiction pour chaque paire
- **Critère :** Données datées de moins de 24h

### SC-03 : Classification à la demande
- **Pré-condition :** Utilisateur connecté, API ML disponible
- **Scénario :** Sélectionne BTCUSDT, daily, 3 prédictions
- **Post-condition :** Affiche 3 lignes avec date, classe, confiance
- **Critère :** Chaque confiance est entre 0 et 100%

### SC-04 : Gestion des erreurs API
- **Pré-condition :** API ML indisponible
- **Scénario :** Utilisateur soumet une classification
- **Post-condition :** Message d'erreur explicite (pas de 500)
- **Critère :** L'utilisateur comprend que le service est temporairement indisponible

---

## 6. Objectifs d'accessibilité (WCAG 2.1 AA)

| Critère WCAG | Implémentation |
|-------------|----------------|
| 1.1.1 Contenu non textuel | Attributs `alt` sur les images, `aria-label` sur les boutons |
| 1.3.1 Information et relations | Structure sémantique HTML5 (`<nav>`, `<main>`, `<table>`) |
| 1.4.3 Contraste minimum | Ratio 4.5:1 texte/fond (Bootstrap + surcharges CSS) |
| 2.1.1 Clavier | Navigation complète au clavier (formulaires, liens) |
| 2.4.1 Contourner des blocs | Lien "Aller au contenu" en haut de page |
| 3.3.1 Identification des erreurs | Messages d'erreur associés aux champs (Django form errors) |
| 4.1.2 Nom, rôle, valeur | Utilisation correcte des éléments de formulaire natifs |

---

## 7. Contraintes techniques

| Contrainte | Valeur |
|-----------|--------|
| Temps de réponse max (dashboard) | < 3 secondes |
| Temps de réponse max (classification) | < 10 secondes |
| Disponibilité cible | 99% (hors maintenance planifiée) |
| Navigateurs supportés | Chrome, Firefox, Safari (versions récentes) |
| Responsive design | Desktop + tablette (min 768px) |
| Authentification | Session Django (cookie) + JWT inter-services |
