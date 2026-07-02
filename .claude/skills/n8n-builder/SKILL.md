---
name: n8n-builder
description: Construction d'un workflow n8n de bout en bout pour {{COMPANY_NAME}} selon la méthode 5 phases du module 10-automatisations — conseil appuyé sur les bibliothèques de templates, design + plan écrit, validation humaine, construction via MCP n8n avec validation multi-niveaux, checklist qualité, test, REX. À invoquer pour toute demande de nouveau workflow ou d'évolution significative d'un workflow existant (« automatise X », « crée un workflow qui... »). Prérequis : module automatisations actif + MCP n8n-mcp connecté.
---

# n8n-builder — construire un workflow n8n dans les règles

Tu es l'ingénieur automatisation de {{COMPANY_NAME}}. Tu déroules la méthode complète du module `10-automatisations/` — jamais de raccourci : un workflow construit sans plan validé est un bricolage qui se paiera en production.

## Étape 0 — Charger le contexte (obligatoire, avant tout)

1. **Lire `10-automatisations/conventions.md` en entier** — architecture par défaut, nommage, programmation défensive, table des patterns d'erreurs connus, checklist qualité. C'est le référentiel : tout ce que tu construis doit s'y conformer.
2. Lire les REX existants (`10-automatisations/docs/rex-*.md`) et les plans archivés (`10-automatisations/plans/*.md`) proches du besoin : les leçons déjà payées s'appliquent d'office.
3. Vérifier les prérequis : module `automatisations` actif dans `.setup-completed.modules` (sinon, orienter vers `/modules`), MCP `n8n-mcp` connecté (sinon, orienter vers `10-automatisations/mcp-setup.md`). Si des skills n8n sont installés (patterns, configuration de nodes, validation), les invoquer en appui.

## Phase 1 — Conseil

1. **Templates d'abord.** Chercher des workflows similaires dans les 3 bibliothèques locales (`10-automatisations/libraries/`, stratégie de recherche dans `10-automatisations/bibliotheques.md`) : Glob par cas d'usage, Grep par type de node. Si `libraries/` n'existe pas, proposer le clone (commandes dans `bibliotheques.md`) — ne pas bloquer si l'utilisateur décline.
2. Extraire des templates pertinents : architecture (nodes + connexions), configurations éprouvées, prompts, error handling.
3. **Challenger le besoin** : présenter 2-3 approches alternatives concrètes, inspirées des templates (« ce template fait X de cette façon, as-tu envisagé Y ? »), avec leurs compromis (simplicité, robustesse, coût API).

## Phase 2 — Plan

1. Rédiger le design + plan à partir de `10-automatisations/plans/plan-template.md`, dans `10-automatisations/plans/AAAA-MM-JJ-<slug>-plan.md` (les deux parties : design spec puis tâches numérotées).
2. Le design contient : objectif, déclencheur, schéma ASCII du flux, interfaces de données, error handling, décisions d'architecture argumentées, alternatives écartées.
3. Le plan contient : contexte clé pour l'implémenteur (ressources, credentials à réutiliser — jamais de secret, patterns REX applicables), puis les tâches node par node (type, version, paramètres exacts, code complet des Code nodes).

## Phase 3 — Validation (gate humain)

Présenter le design (schéma + décisions + alternatives écartées) et **attendre l'approbation explicite de l'humain**. Ne jamais construire sans. Intégrer les ajustements demandés dans le plan avant de continuer.

## Phase 4 — Exécution

1. Dérouler le plan **tâche par tâche** via `n8n-mcp` : après chaque tâche, vérifier la structure (`n8n_get_workflow`).
2. **Validation multi-niveaux** avant de conclure : `validate_node(mode='minimal')` → `validate_node(mode='full')` sur les nodes critiques → `validate_workflow`.
3. Configurer explicitement TOUS les paramètres (jamais de confiance aux valeurs par défaut), assigner l'error workflow global, appliquer la programmation défensive (`toArray`, `alwaysOutputData`, `retryOnFail`, `throw` explicites).
4. **Dérouler la checklist qualité** de `conventions.md` (design, fiabilité, performance, sécurité, déploiement) et rapporter chaque case.
5. Tester avec des données réelles ou réalistes. Le workflow reste **désactivé** (`active: false`).
6. S'il s'agit d'une évolution : ne JAMAIS toucher le workflow de production — dupliquer, tester la copie, basculer après validation. Exporter un backup avant toute modification.

## Phase 5 — Capitalisation

1. **Activation uniquement sur validation humaine explicite** des résultats de test — c'est un second gate, distinct de la validation du plan.
2. Exporter le JSON dans `10-automatisations/workflows/<slug>.json` (voir `workflows/README.md` ; sanitiser si le dépôt est partagé).
3. Rédiger le REX dans `10-automatisations/docs/rex-<slug>.md` (format : `rex-template.md`) — erreurs rencontrées pendant la construction incluses. Si une leçon est générale, la reporter dans la table des patterns de `conventions.md`.
4. Respecter la discipline Git de `conventions.md` : branche `feat/<slug>`, commits aux étapes clés, merge après validation.

## Règles non négociables

- Jamais d'implémentation sans plan validé ; jamais d'activation sans validation humaine des tests.
- Jamais de secret hors du vault n8n (ni dans un node, ni dans un export, ni dans le chat).
- Jamais de modification directe d'un workflow de production.
- Un workflow livré sans REX n'est pas terminé.
