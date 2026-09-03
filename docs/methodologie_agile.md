# Méthodologie de conduite de projet — Projet Crypto Certification

## 1. Contexte

Projet individuel, sans équipe formelle — la conduite de projet est adaptée en conséquence
plutôt que de simuler des rituels d'équipe qui n'auraient pas de sens pour un développeur seul
(pas de daily standup avec soi-même, pas de board Kanban multi-colonnes actif à ce jour).

## 2. Outils de pilotage réels

- **Backlog** : GitHub Issues du dépôt `crypto-certification`, plutôt qu'un outil séparé —
  cohérent avec l'hébergement du code. À date, 8 issues ouvertes, toutes des limites assumées
  identifiées pendant les rapports E2/E3 (sécurité ml-api, qualité du modèle, tests
  d'orchestration...) — ce n'est pas un backlog de construction du Bloc4_app, dont le suivi
  s'est fait directement par commit.
- **Branches** : deux branches de travail réelles, `bloc1_data` et `bloc2-bloc3-mise-en-service`,
  divergentes depuis le commit initial du dépôt. Elles ne sont pas encore fusionnées dans `main`
  (`main` est toujours au commit initial) — point à traiter avant une diffusion plus large,
  listé dans le bilan plutôt que caché.
- **Pas de board GitHub Projects actif.** Un board Kanban avait été envisagé (Backlog → In
  Progress → Review → Done) mais n'a jamais été créé dans les faits ; le suivi réel s'est fait
  par les commits et les issues.

## 3. Rythme de travail réel

Pas de cérémonie agile formelle. Le suivi s'est fait par itérations courtes, chaque commit
correspondant à un incrément livrable et testé avant de passer au suivant — la convention de
message (`feat(bloc4): ...`, `fix(bloc4): ...`, `test(bloc4): ...`) sert de journal de bord :

| Commit | Contenu |
|--------|---------|
| `feat(bloc4): monitorage de dérive du modèle en production (C11)` | dashboard/metrics.py + vue monitoring |
| `fix(bloc4): timeout + retry sur token expiré dans ForecastService (C10)` | robustesse de l'intégration ml-api |
| `test(bloc4): ajoute les tests de monitoring_view oubliés au commit C11` | complète la couverture après coup |

## 4. Définition of Done (DoD) réelle

Une tâche est considérée terminée lorsque :
1. Le code est fonctionnel et testé (suite pytest verte en local).
2. Le commit est explicite sur le bloc et la compétence visée.
3. La documentation associée (README du module concerné) est mise à jour si le comportement change.

## 5. Limite assumée

Le choix initial (board Kanban, rituels hebdomadaires, branche par bloc fusionnée via PR après
revue) reflétait un mode de fonctionnement d'équipe qui ne correspond pas à la réalité d'un
projet individuel de certification. Cette version documente ce qui a réellement eu lieu plutôt
que ce qui avait été initialement prévu.
