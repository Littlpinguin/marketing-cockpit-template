# 10-automatisations — n8n, moteur d'automatisation du copilot

> **Module optionnel.** Ce module transforme le copilot marketing en système partiellement autonome : les tâches répétitives (dépôt des transcriptions, veille, reporting, notifications d'erreurs) tournent en tâche de fond dans n8n, et Claude Code pilote l'instance via MCP.

## Pourquoi n8n

[n8n](https://n8n.io) est un orchestrateur de workflows open source, self-hostable, avec plus de 400 intégrations natives (email, Google Workspace, Notion, Slack, CRM, LLM...). Dans ce template, il joue trois rôles :

1. **Alimenter `00-intel/`** : chaque transcription de meeting est analysée, classée et déposée automatiquement dans `00-intel/inbox/` — c'est le flux qui rend le copilot « au courant » de ce qui se passe dans l'entreprise.
2. **Automatiser les process marketing récurrents** : veille hebdomadaire, rapport quotidien de métriques, rappels de statuts du calendrier éditorial.
3. **Servir de moteur au module `12-acquisition/`** (pipeline de prospection B2B) si vous l'activez.

## Modes d'hébergement

| Mode | Pour qui | Coût d'ordre de grandeur |
|---|---|---|
| **Self-hosted sur VPS** (recommandé) | Contrôle total, données chez vous, exécutions illimitées | ~5-15 €/mois (VPS type Hostinger, Contabo, OVH, Scaleway...) |
| **n8n Cloud** | Zéro maintenance, mise en route en 10 minutes | À partir de ~24 €/mois, exécutions plafonnées |

L'auteur du template utilise un VPS Hostinger avec n8n en Docker — voir `INSTALL.md` pour le pas à pas complet (Docker, HTTPS, authentification, error workflow global).

## Connexion depuis le copilot

Deux briques relient Claude Code à votre instance n8n :

1. **Variables d'environnement** dans `.env` (jamais committées) :

   ```bash
   N8N_API_URL="https://{{VOTRE_INSTANCE_N8N}}/api/v1"
   N8N_API_KEY="{{VOTRE_CLE_API_N8N}}"
   ```

   La clé API se génère dans n8n : *Settings → n8n API → Create an API key*.

2. **Le serveur MCP [n8n-mcp](https://github.com/czlonkowski/n8n-mcp)** déclaré dans `.mcp.json` : il donne à Claude Code la capacité de créer, lire, valider et tester des workflows directement sur l'instance. Configuration détaillée dans `INSTALL.md`.

## Contenu du module

| Fichier | Rôle |
|---|---|
| `INSTALL.md` | Installation n8n sur VPS + configuration du MCP + sécurité |
| `conventions.md` | Standards de conception des workflows (architecture, nommage, erreurs, checklist qualité) |
| `workflows/` | 4 workflows de référence, génériques et sanitisés, prêts à importer |
| `workflows/README.md` | Mode d'emploi : placeholders à remplacer, credentials à recréer |
| `scripts/backup-workflows.sh` | Export quotidien de tous les workflows via l'API n8n |
| `rex-template.md` | Format de capitalisation des leçons apprises (REX) après chaque mise en production |

## Les 4 workflows de référence

| Workflow | Déclencheur | Ce qu'il fait |
|---|---|---|
| `error-handler.json` | Erreur dans n'importe quel workflow | Notification email HTML avec workflow, node en erreur, message, lien d'exécution. **À installer en premier.** |
| `meeting-transcript-to-intel.json` | Webhook (outil de transcription) | Analyse LLM de la transcription → classification (client / prospect / interne / veille) → note structurée déposée dans `00-intel/inbox/` |
| `veille-hebdo.json` | Cron (lundi 8h) | Recherche d'actualités sur vos thèmes → synthèse et scoring LLM → note de veille + email récap |
| `daily-report.json` | Cron (jours ouvrés 18h) | Collecte de métriques → agrégation → rapport HTML envoyé par email |

## Ordre de mise en route

1. Installer n8n (`INSTALL.md`).
2. Importer et activer `error-handler.json`, noter son ID.
3. Importer les autres workflows, remplacer les placeholders (`workflows/README.md`), assigner l'error workflow, recréer les credentials **dans le vault n8n uniquement**.
4. Tester chaque workflow avec des données réalistes, workflow **désactivé** jusqu'à validation.
5. Planifier `scripts/backup-workflows.sh` en cron quotidien.
6. Après chaque mise en production : rédiger un REX (`rex-template.md`).

## Règle de sécurité non négociable

**Aucun secret ne sort du vault n8n.** Les credentials (clés API, OAuth, SMTP) vivent exclusivement dans le gestionnaire de credentials chiffré de n8n. Les exports JSON committés dans `workflows/` ne contiennent que des placeholders — jamais de token, d'ID de compte ni d'email réel. Voir `SECURITY.md` à la racine du repo.
