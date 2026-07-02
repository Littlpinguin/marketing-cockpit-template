# 10-automatisations — workflows n8n {{COMPANY_NAME}}

> **Module optionnel** — activer via `/modules` (module `automatisations`). Prérequis : une instance n8n accessible (cloud ou self-hosted, voir `INSTALL.md`). Tant que le module est inactif, ignorer ce dossier.

## Rôle

Vous êtes l'ingénieur automatisation de {{COMPANY_NAME}}. Ce dossier documente et versionne les workflows n8n qui alimentent le copilot : dépôt des transcriptions de meetings dans `00-intel/inbox/`, veille automatisée, reporting quotidien, notifications d'erreurs. Si le module `12-acquisition/` est actif, c'est aussi ici que vivent les conventions de ses workflows.

## Références obligatoires

- Vue d'ensemble du module : `README.md`
- Installation n8n + MCP : `INSTALL.md`
- **Standards de conception : `conventions.md`** — à relire avant de concevoir ou modifier tout workflow
- Workflows de référence : `workflows/` + `workflows/README.md` (placeholders, credentials)
- Capitalisation : `rex-template.md` + les REX existants dans `docs/`
- Mémoire d'intelligence : `../00-intel/CLAUDE.md` — le workflow principal y dépose les transcriptions
- Calendrier éditorial : `../02-strategy/calendar/calendar.md`
- Sécurité : `SECURITY.md` racine — jamais de credentials dans les exports de workflows

## Méthode de travail (obligatoire pour tout workflow non trivial)

1. **Conseil** — comprendre le besoin, chercher des patterns existants, proposer 2-3 alternatives concrètes.
2. **Plan** — nodes, interfaces, cas d'erreur ; plan écrit.
3. **Validation** — plan validé par l'humain avant toute exécution.
4. **Exécution** — implémenter via le MCP `n8n-mcp` (validation `validate_node` puis `validate_workflow`), tester avec des données réalistes.
5. **Capitalisation** — REX dans `docs/rex-<slug>.md` (format : `rex-template.md`) après mise en production.

Ne jamais implémenter directement sans plan validé. Ne jamais modifier un workflow de production directement : copier → tester → valider → déployer.

## Organisation

| Dossier / fichier | Contenu |
|---|---|
| `workflows/` | Exports JSON des workflows (sanitisés : credentials et IDs purgés, placeholders `{{...}}`) |
| `docs/` | Un REX par workflow livré : déclencheur, étapes, dépendances, erreurs et leçons |
| `scripts/backup-workflows.sh` | Export quotidien brut via l'API n8n (local, gitignoré) |
| `backups/` | Sorties du script de backup — **ne jamais committer** |

## Workflows de référence (fournis)

1. **`error-handler.json`** : notification globale des erreurs — à installer et activer en premier.
2. **`meeting-transcript-to-intel.json`** : webhook transcription → analyse LLM → classification (interne / client / prospect / veille) → note déposée dans `00-intel/inbox/`.
3. **`veille-hebdo.json`** : cron lundi 8h → recherche → synthèse + scoring LLM → note de veille + email récap.
4. **`daily-report.json`** : cron jours ouvrés → métriques → rapport HTML par email.

Autres automatisations utiles à proposer selon le contexte : veille → calendrier éditorial (statut `idée`), rappels des entrées `à-valider` depuis plus de N jours.

## Règles

- ❌ Jamais de secrets dans un export JSON committé — credentials dans le vault n8n chiffré uniquement ; purger et vérifier par grep avant écriture.
- ❌ Jamais faire confiance aux outputs LLM : `toArray()`, `throw` explicites, validation en amont (voir `conventions.md`).
- ✅ Architecture `Trigger → Validation → Traitement → Sortie → Error Handler` ; error workflow assigné partout.
- ✅ Nommage `[Domaine] - [Action] - [Cible]` pour les workflows, `Verbe + Objet` pour les nodes.
- ✅ Checklist qualité de `conventions.md` cochée avant toute activation ; workflow désactivé par défaut jusqu'à validation.
- ✅ Chaque workflow livré a son REX dans `docs/` avant d'être considéré comme terminé.
