# 10-automatisations — créer vos automatisations n8n depuis Claude

> **Module optionnel.** Ce module fait de Claude Code votre ingénieur automatisation : **créer, déboguer et faire évoluer vos workflows n8n directement depuis Claude**, avec une méthode complète — conseil appuyé sur 5 100+ templates de référence → plan validé par vous → construction et validation via MCP → capitalisation (REX). C'est le portage fidèle d'un système qui tourne en production réelle.

## Le système en 4 briques

```
Claude Code
    |
    +-- n8n-mcp ----------> votre instance n8n (CRUD workflows, exécutions, validation)
    |
    +-- conventions.md ---> le référentiel : architecture, defensive programming,
    |                       patterns d'erreurs connus, checklist qualité
    |
    +-- libraries/ -------> 5 100+ workflows de référence (3 repos clonés localement,
    |                       consultés AVANT de construire — bibliotheques.md)
    |
    +-- plans/ + REX -----> mémoire du système : designs validés, leçons apprises
```

| Brique | Rôle | Fichier |
|---|---|---|
| **n8n** (instance) | Exécute les workflows — self-hosted ou cloud | `INSTALL.md` |
| **n8n-mcp** (serveur MCP) | Donne à Claude un accès outillé à l'instance | `mcp-setup.md` |
| **Conventions** | Standards de conception + patterns d'erreurs issus de la production | `conventions.md` |
| **Bibliothèques de templates** | 5 100+ workflows réels pour la phase conseil | `bibliotheques.md` |
| **Plans** | Design spec + tâches numérotées, validés avant exécution | `plans/` |
| **REX** | Retours d'expérience — chaque erreur payée une seule fois | `rex-template.md` |

## La méthode — 5 phases

```
1. CONSEIL         Recherche de templates similaires dans les bibliothèques,
                   proposition d'architectures alternatives
2. PLAN            Design détaillé (nodes, connexions, prompts, error handling)
3. VALIDATION      Relecture et approbation du plan par VOUS avant exécution
4. EXÉCUTION       Construction dans n8n via MCP, validation multi-niveaux, tests
5. CAPITALISATION  Export JSON versionné, REX, mise à jour du repo
```

Architecture par défaut de tout workflow : `Trigger → Validation → Traitement → Sortie → Error Handler`.

## Skills et agent fournis (ce que le module automatise)

La méthode ci-dessus n'est pas qu'une documentation : elle est outillée.

| Outil | Ce qu'il automatise |
|---|---|
| skill **`n8n-builder`** | Déroule la méthode complète de bout en bout : consultation des bibliothèques → design + plan → **validation humaine** → construction via `n8n-mcp` → checklist qualité → test → REX. À invoquer pour tout nouveau workflow. |
| skill **`n8n-audit`** | Passe un workflow existant au crible des conventions : architecture, error handling, nommage, programmation défensive, secrets hors vault, `alwaysOutputData`… Rend un rapport de conformité actionnable. |
| agent **`n8n-debugger`** | Lit les exécutions en échec via l'API n8n, croise avec la table des patterns d'erreurs connus, rend un diagnostic + correctif proposé (jamais appliqué sans votre validation). |

Règle commune : **aucun workflow n'est activé ni modifié en production sans validation humaine explicite.**

## Ce que le module fait tourner pour le copilot

1. **Alimenter `00-intel/`** : chaque transcription de meeting est analysée, classée et déposée dans `00-intel/inbox/` — le flux qui rend le copilot « au courant ».
2. **Automatiser les process marketing récurrents** : veille hebdomadaire, rapport quotidien, rappels du calendrier éditorial.
3. **Servir de moteur au module `12-acquisition/`** (prospection B2B) si vous l'activez.
4. **Et tout ce que vous voulez construire ensuite** — c'est le but de la méthode.

## Contenu du module

| Fichier / dossier | Rôle |
|---|---|
| `INSTALL.md` | Installation n8n sur VPS (Docker, HTTPS, auth) + error workflow global + sécurité |
| `mcp-setup.md` | Le bloc `n8n-mcp` exact à coller dans le `.mcp.json` **local** (gitignoré — valeurs réelles, copié depuis `.mcp.json.example`) |
| `conventions.md` | **Le cœur du module** : méthode, architecture, nommage, erreurs, patterns connus, checklist |
| `bibliotheques.md` | Les 3 bibliothèques de templates : rôle, licences, clone, workflow de consultation |
| `plans/` | Méthode des plans + `plan-template.md` (design spec + tâches numérotées) |
| `workflows/` | Copie JSON de VOS workflows en production (versionnée dans votre fork privé) |
| `workflows/examples/` | 4 workflows génériques sanitisés pour démarrer (error handler, intel, veille, reporting) |
| `rex-template.md` | Format de capitalisation + 3 leçons réelles pré-remplies en exemple |
| `scripts/backup-workflows.sh` | Export quotidien de tous les workflows via l'API n8n |

## Modes d'hébergement

| Mode | Pour qui | Coût d'ordre de grandeur |
|---|---|---|
| **Self-hosted sur VPS** (recommandé) | Contrôle total, données chez vous, exécutions illimitées | ~5-15 €/mois (VPS type Hostinger, Contabo, OVH, Scaleway...) |
| **n8n Cloud** | Zéro maintenance, mise en route en 10 minutes | À partir de ~24 €/mois, exécutions plafonnées |

## Ordre de mise en route

1. Installer n8n (`INSTALL.md`) — ou créer un compte n8n Cloud.
2. Brancher Claude : `.env` pour les scripts + bloc `n8n-mcp` (valeurs réelles) dans le `.mcp.json` local non versionné (`mcp-setup.md`), vérifier avec `/mcp`.
3. Cloner les bibliothèques de templates dans `libraries/` (`bibliotheques.md`) — dossier gitignoré.
4. Importer et activer `workflows/examples/error-handler.json`, noter son ID (c'est le `{{ERROR_WORKFLOW_ID}}` de tous les autres workflows).
5. Importer les autres exemples utiles (`workflows/examples/README.md`), credentials **dans le vault n8n uniquement**, tester, activer.
6. Planifier `scripts/backup-workflows.sh` en cron quotidien.
7. Construire votre premier workflow sur mesure avec le skill `n8n-builder`.

## Règle de sécurité non négociable

**Aucun secret ne sort du vault n8n.** Les credentials (clés API, OAuth, SMTP) vivent exclusivement dans le gestionnaire de credentials chiffré de n8n. Les exports JSON committés dans un dépôt partagé ne contiennent que des placeholders — jamais de token, d'ID de compte ni d'email réel. Voir `SECURITY.md` à la racine du repo et la section Sécurité de `conventions.md`.
