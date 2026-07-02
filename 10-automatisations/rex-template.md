# REX — {{NOM_DU_WORKFLOW}}

> **Format de capitalisation des leçons apprises.** Copier ce fichier dans `docs/rex-{{slug-du-workflow}}.md` après chaque mise en production ou incident significatif. Objectif : que chaque erreur rencontrée ne soit payée qu'une seule fois. Les REX accumulés deviennent la mémoire technique du module — Claude les lit avant de concevoir un nouveau workflow.

**Workflow ID** : `{{WORKFLOW_ID}}`
**Date** : {{AAAA-MM-JJ}}
**Statut** : Brouillon | En test | En production | Retiré

## Description

Ce que fait le workflow, en 3-6 lignes : déclencheur, étapes principales, sorties. Suffisamment précis pour qu'un lecteur qui n'a jamais ouvert le workflow comprenne son rôle dans le système.

## Erreurs rencontrées et corrections

> Une sous-section par erreur. La **leçon** est la partie la plus importante : c'est elle qui est réutilisable.

### 1. {{Titre court de l'erreur}}

**Problème** : ce qui ne fonctionnait pas, techniquement (node concerné, paramètre, comportement observé).

**Symptôme** : ce qu'on voyait de l'extérieur (résultat erroné, flux bloqué, hallucination du LLM, notification absente...). Utile pour reconnaître le même problème plus tard.

**Correction** : ce qui a été changé, précisément (paramètre, node ajouté, code).

**Leçon** : la règle générale à retenir, formulée pour être applicable à d'autres workflows. Si la leçon est vraiment générale, la reporter aussi dans `conventions.md`.

### 2. ...

## Décisions d'architecture

| Décision | Raison |
|---|---|
| {{Choix technique retenu}} | {{Pourquoi, et quelle alternative a été écartée}} |
| | |

## Points de vigilance pour la maintenance

- Dépendances externes à surveiller (credentials à renouveler, structure attendue d'un document source, dossier surveillé, quota API...)
- Hypothèses fragiles (format d'un payload webhook, champ optionnel côté source...)
- Ce qu'il faut vérifier avant toute modification future

## Métriques (optionnel)

- Fréquence d'exécution constatée :
- Taux d'erreur depuis la mise en production :
- Temps gagné estimé par exécution :
