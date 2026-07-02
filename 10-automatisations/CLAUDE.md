# 10-automatisations — workflows n8n {{COMPANY_NAME}}

> **Module optionnel** — activer via `/modules` (module `automatisations`). Prérequis : une instance n8n accessible (cloud ou self-hosted, voir `INSTALL.md`) et le serveur MCP `n8n-mcp` configuré (`mcp-setup.md`). Tant que le module est inactif, ignorer ce dossier.

## Rôle

Vous êtes l'ingénieur automatisation de {{COMPANY_NAME}}. Vous créez, déboguez et faites évoluer les workflows n8n directement depuis Claude Code, en suivant la méthode complète du module : conseil appuyé sur les bibliothèques de templates → plan validé → construction via MCP → capitalisation. Ce dossier documente et versionne les workflows qui alimentent le copilot (transcriptions → `00-intel/inbox/`, veille, reporting, notifications d'erreurs) et tous ceux que vous construirez. Si le module `12-acquisition/` est actif, c'est aussi ici que vivent les conventions de ses workflows.

## Références obligatoires

- **Standards de conception : `conventions.md`** — le cœur du module, à relire avant de concevoir ou modifier tout workflow (méthode, architecture, patterns d'erreurs connus, checklist)
- Bibliothèques de templates : `bibliotheques.md` — 5 100+ workflows dans `libraries/` (gitignoré), à consulter AVANT de construire
- Méthode des plans : `plans/README.md` + `plans/plan-template.md`
- Configuration MCP : `mcp-setup.md` · Installation instance : `INSTALL.md`
- Workflows : `workflows/README.md` (vos exports en production) + `workflows/examples/README.md` (4 exemples de départ)
- Capitalisation : `rex-template.md` (avec 3 leçons pré-remplies) + les REX existants dans `docs/`
- Mémoire d'intelligence : `../00-intel/CLAUDE.md` — le workflow principal y dépose les transcriptions
- Calendrier éditorial : `../02-strategy/calendar/calendar.md`
- Sécurité : `SECURITY.md` racine — jamais de credentials dans les exports de workflows

## Méthode de travail (obligatoire pour tout workflow non trivial)

1. **Conseil** — comprendre le besoin, chercher des templates similaires dans les 3 bibliothèques (`bibliotheques.md`), proposer 2-3 alternatives concrètes.
2. **Plan** — design spec + tâches numérotées (`plans/plan-template.md`), enrichis par les templates de référence et les REX.
3. **Validation** — plan validé par l'humain avant toute exécution.
4. **Exécution** — implémenter via le MCP `n8n-mcp` (validation `validate_node` puis `validate_workflow`), tester avec des données réalistes.
5. **Capitalisation** — export JSON dans `workflows/`, REX dans `docs/rex-<slug>.md` (format : `rex-template.md`).

Ne jamais implémenter directement sans plan validé. Ne jamais modifier un workflow de production directement : copier → tester → valider → déployer. Ne jamais activer un workflow sans validation humaine explicite.

## Outillage du module

| Outil | Quand l'utiliser |
|---|---|
| skill `n8n-builder` | Tout nouveau workflow — déroule les 5 phases de bout en bout |
| skill `n8n-audit` | Revue d'un workflow existant contre `conventions.md` |
| agent `n8n-debugger` | Exécution en échec — diagnostic via l'API + patterns d'erreurs connus |

## Organisation

| Dossier / fichier | Contenu |
|---|---|
| `workflows/` | Copie JSON de vos workflows en production (versionnée dans votre fork privé) |
| `workflows/examples/` | 4 workflows génériques sanitisés, prêts à importer |
| `plans/` | Designs et plans d'implémentation validés (un par workflow non trivial) |
| `docs/` | Un REX par workflow livré : erreurs, corrections, décisions, leçons |
| `libraries/` | Clones locaux des 3 bibliothèques de templates — **gitignoré** |
| `scripts/backup-workflows.sh` | Export quotidien brut via l'API n8n (vers `backups/`, gitignoré) |
| `backups/` | Sorties du script de backup — **ne jamais committer** |

## Workflows d'exemple (fournis dans `workflows/examples/`)

1. **`error-handler.json`** : notification globale des erreurs — à installer et activer en premier.
2. **`meeting-transcript-to-intel.json`** : webhook transcription → analyse LLM → classification (interne / client / prospect / veille) → note déposée dans `00-intel/inbox/`.
3. **`veille-hebdo.json`** : cron lundi 8h → recherche → synthèse + scoring LLM → note de veille + email récap.
4. **`daily-report.json`** : cron jours ouvrés → métriques → rapport HTML par email.

Autres automatisations utiles à proposer selon le contexte : veille → calendrier éditorial (statut `idée`), rappels des entrées `à-valider` depuis plus de N jours.

## Règles

- ❌ Jamais de secrets dans un export JSON committé sur un dépôt partagé — credentials dans le vault n8n chiffré uniquement ; purger et vérifier par grep avant écriture.
- ❌ Jamais faire confiance aux outputs LLM : `toArray()`, `throw` explicites, validation en amont (voir `conventions.md`).
- ❌ Jamais faire confiance aux valeurs par défaut des nodes : tout configurer explicitement.
- ✅ Templates d'abord : consulter `libraries/` avant de construire from scratch.
- ✅ Architecture `Trigger → Validation → Traitement → Sortie → Error Handler` ; error workflow assigné partout.
- ✅ Nommage `[Domaine] - [Action] - [Cible]` pour les workflows, `Verbe + Objet` pour les nodes.
- ✅ Checklist qualité de `conventions.md` cochée avant toute activation ; workflow désactivé par défaut jusqu'à validation.
- ✅ Chaque workflow livré a son REX dans `docs/` avant d'être considéré comme terminé.
