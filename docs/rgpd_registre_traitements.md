# Registre des Traitements de Données Personnelles (RGPD)

**Responsable de traitement :** Développeur du projet (certification)  
**Date de création :** Mai 2026  
**Dernière mise à jour :** Mai 2026

---

## 1. Inventaire des traitements

### Traitement T1 — Gestion des comptes utilisateurs (API Bloc1)

| Champ | Valeur |
|-------|--------|
| **Finalité** | Authentification et contrôle d'accès à l'API de données |
| **Base légale** | Intérêt légitime (sécurisation de l'accès) |
| **Catégories de personnes** | Utilisateurs techniques (scripts, services) |
| **Données collectées** | Username, mot de passe hashé, rôle, statut |
| **Données sensibles** | Non |
| **Source des données** | Saisie par l'administrateur |
| **Destinataires** | Service d'authentification interne uniquement |
| **Transfert hors UE** | Non (hébergement local / Docker) |
| **Durée de conservation** | Durée de vie du projet |
| **Mesures de sécurité** | Hashage bcrypt, JWT avec expiration, HTTPS |

### Traitement T2 — Gestion des comptes utilisateurs (Application Django)

| Champ | Valeur |
|-------|--------|
| **Finalité** | Inscription et connexion des utilisateurs finaux |
| **Base légale** | Consentement (inscription volontaire) |
| **Catégories de personnes** | Utilisateurs de la plateforme web |
| **Données collectées** | Username, mot de passe hashé (Django auth), email (optionnel) |
| **Données sensibles** | Non |
| **Source des données** | Formulaire d'inscription |
| **Destinataires** | Application Django uniquement |
| **Transfert hors UE** | Non |
| **Durée de conservation** | Jusqu'à suppression du compte par l'utilisateur |
| **Mesures de sécurité** | Hashage PBKDF2 (Django), session cookie sécurisé, CSRF |

### Traitement T3 — Données de marché crypto (OHLCV)

| Champ | Valeur |
|-------|--------|
| **Finalité** | Stockage de données de marché pour l'entraînement ML |
| **Base légale** | N/A — pas de données personnelles |
| **Catégories de données** | Cours OHLCV (Open, High, Low, Close, Volume) |
| **Source** | API Binance, CoinMarketCap, fichiers CSV historiques |
| **Commentaire** | Ces données sont publiques et ne constituent pas des données personnelles au sens du RGPD |

---

## 2. Analyse de conformité

### Données personnelles identifiées

| Donnée | Table | Qualification RGPD |
|--------|-------|-------------------|
| `username` | `users` (Bloc1) | Donnée identifiante si pseudonyme réel |
| `password_hashed` | `users` (Bloc1) | Donnée technique (non réversible) |
| `username` | `auth_user` (Django) | Donnée identifiante |
| `email` | `auth_user` (Django) | Donnée personnelle directe |
| Cours crypto | `ohlcv_*` | Pas une donnée personnelle |
| Prédictions | `predictions_*` | Pas une donnée personnelle |

### Évaluation des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| Fuite de mots de passe | Faible | Élevé | Hashage irréversible (bcrypt/PBKDF2) |
| Accès non autorisé aux données | Faible | Moyen | JWT avec expiration + @login_required |
| Perte de données | Faible | Faible | Volume Docker persistant + backup possible |

---

## 3. Procédures de tri et de conformité

### 3.1 Minimisation des données

- Seules les données strictement nécessaires sont collectées (username + password)
- Pas de collecte d'adresse IP, de géolocalisation, ou de données comportementales
- Les données de marché sont publiques et anonymes

### 3.2 Droit d'accès (Article 15 RGPD)

**Procédure :** L'utilisateur peut consulter son profil via l'interface Django. En cas de demande formelle, l'administrateur exporte les données via Django admin.

**Fréquence de vérification :** À la demande

### 3.3 Droit de suppression (Article 17 RGPD)

**Procédure — Application Django (T2) :**
1. L'utilisateur demande la suppression de son compte
2. L'administrateur supprime l'entrée dans `auth_user` (Django)
3. Les sessions associées sont invalidées
4. Confirmation envoyée à l'utilisateur

**Délai :** 30 jours maximum après la demande

**Procédure — Compte API Bloc1 (T1) :** suppression en libre-service, sans intervention d'un administrateur. L'utilisateur authentifié appelle `DELETE /api/v1/authentification/account` ; le compte est supprimé immédiatement en base.

**Délai :** immédiat (temps de traitement de la requête HTTP)

### 3.4 Droit à la portabilité (Article 20 RGPD)

**Procédure :** Export JSON des données du compte via Django admin.

**Format :** JSON structuré

### 3.5 Durée de conservation

| Type de donnée | Durée | Action à l'expiration |
|----------------|-------|-----------------------|
| Comptes utilisateurs actifs | Illimitée (tant que le compte est actif) | — |
| Comptes inactifs (> 12 mois) | 12 mois après dernière connexion | Notification puis suppression |
| Logs applicatifs | 90 jours | Rotation automatique |
| Données de marché | Illimitée | Pas de données personnelles |

### 3.6 Fréquence des contrôles de conformité

| Contrôle | Fréquence |
|----------|-----------|
| Revue des accès (qui a accès à quoi) | Trimestrielle |
| Vérification des durées de conservation | Semestrielle |
| Audit des mesures de sécurité | Annuelle |
| Mise à jour du registre | À chaque modification du système |

---

## 4. Mesures de sécurité techniques

| Mesure | Implémentation |
|--------|---------------|
| Chiffrement des mots de passe | bcrypt (Bloc1), PBKDF2 (Django) |
| Authentification | JWT avec expiration (Bloc1/Bloc3), sessions Django |
| Protection CSRF | Middleware Django activé |
| Contrôle d'accès | `@login_required`, rôles utilisateur |
| Isolation réseau | Docker network (services non exposés publiquement sauf ports nécessaires) |
| Journalisation | Logging Python dans chaque bloc |
| Sauvegarde | Volumes Docker persistants |

---

## 5. Sous-traitants

| Sous-traitant | Service | Données concernées | Localisation |
|--------------|---------|-------------------|-------------|
| Aucun | — | — | — |

**Note :** L'ensemble du traitement est réalisé en local (Docker auto-hébergé). Aucune donnée personnelle n'est transmise à un tiers.

Exception : l'appel à l'API Anthropic (Bloc2, benchmark LLM) ne transmet aucune donnée personnelle — uniquement des données de marché publiques.
