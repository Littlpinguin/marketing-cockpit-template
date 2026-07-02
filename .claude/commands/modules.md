---
name: modules
description: Active ou désactive les modules optionnels du copilot (video, automatisations, reporting, acquisition, veille, publication-sociale, espace-client). Vérifie les prérequis de chaque module, enregistre l'état dans .setup-completed et pilote le chargement conditionnel.
---

# /modules — activer / désactiver les modules optionnels

Charger d'abord la skill `copilot-setup`.

## Intention

Le copilot v2 est composé d'un **cœur** (01-brand → 07-events, 09-seo, 02-strategy/calendar, 00-intel en lecture) toujours actif, et de **modules optionnels** qu'on active seulement si l'entreprise en a l'usage et les prérequis. Cette commande est le seul endroit où l'on change l'état d'un module.

Commande réentrante : relancée, elle affiche l'état courant et demande quoi changer.

## Registre des modules

| Module | Dossier / périmètre | Prérequis à vérifier |
|---|---|---|
| `video` | `08-video/` | macOS (`uname -s` == `Darwin`) **et** Palmier Pro installé (demander confirmation à l'utilisateur ; vérifier l'application si un chemin est fourni) |
| `automatisations` | `10-automatisations/` | Instance n8n accessible : `N8N_BASE_URL` (+ `N8N_API_KEY`) présents dans `.env`, test de reachability (GET `<base>/healthz` ou équivalent) |
| `reporting` | `11-reporting/` | Au moins une source de données configurée via `/tools-setup` (GA4/Search Console, Postiz ou outil emailing) |
| `acquisition` | `12-acquisition/` | Instance n8n (comme `automatisations`) ; si scraping : compte Apify (`APIFY_TOKEN` dans `.env`) |
| `veille` | Alimentation de `00-intel/` + backlog d'idées du calendrier | `00-intel/` présent ; recommandé : module `automatisations` actif pour l'alimentation n8n |
| `publication-sociale` | Push des posts validés vers les réseaux | Compte Postiz : `POSTIZ_API_KEY` (+ URL d'instance si self-hosted) dans `.env` |
| `espace-client` | Partage de présentations / dashboards protégés par code | Accès FTP : `FTP_HOST`, `FTP_USER`, `FTP_PASSWORD`, `FTP_REMOTE_PATH` dans `.env` (configurés via `/tools-setup`) |

## Flux

### Étape 1 — État courant

1. Lire `.setup-completed`. S'il n'existe pas : avertir que le setup n'est pas terminé (`/start-copilot`) et proposer de continuer quand même (l'état sera repris par `/validate-setup`).
2. Afficher un tableau : module, état (actif / inactif / jamais configuré), prérequis OK / manquants.

### Étape 2 — Choix de l'utilisateur

Demander quel(s) module(s) activer ou désactiver. Une décision à la fois (invariant `copilot-setup` : une étape par message).

### Étape 3 — Vérification des prérequis (à l'activation)

Pour chaque module à activer, vérifier les prérequis du registre ci-dessus :

- **Présence des variables `.env`** : présence uniquement, ne jamais lire ni afficher les valeurs.
- **Reachability** : tests non destructifs seulement (ping HTTP, `--help`).
- **Gate de confidentialité** : si le module touche des données clients (`veille`, `acquisition`, `reporting` avec GA4/CRM), afficher le gate de confidentialité défini dans `/tools-setup` et obtenir la confirmation du plan Claude utilisé avant d'activer.

Si un prérequis manque : refuser l'activation, expliquer quoi faire (souvent : passer par `/tools-setup` pour configurer le connecteur), proposer de réessayer ensuite.

### Étape 4 — Écriture de l'état

Mettre à jour la clé `modules` de `.setup-completed` (créer la clé si absente) :

```json
"modules": {
  "video":                { "enabled": false, "checked_at": "ISO 8601" },
  "automatisations":      { "enabled": true,  "checked_at": "ISO 8601" },
  "reporting":            { "enabled": false, "checked_at": "ISO 8601" },
  "acquisition":          { "enabled": false, "checked_at": "ISO 8601" },
  "veille":               { "enabled": true,  "checked_at": "ISO 8601" },
  "publication-sociale":  { "enabled": false, "checked_at": "ISO 8601" },
  "espace-client":        { "enabled": true,  "checked_at": "ISO 8601" }
}
```

Présenter le diff avant écriture. Ne rien écrire d'autre dans `.setup-completed`.

### Étape 5 — Chargement conditionnel

Le contrat de chargement, appliqué par toutes les sessions :

- **Module actif** → le `CLAUDE.md` du dossier concerné fait foi ; ses workflows sont disponibles ; `/health-check` vérifie ses prérequis à chaque passage.
- **Module inactif** → ne pas lire ni appliquer le `CLAUDE.md` du module, ne pas proposer ses workflows, ne pas exiger ses variables `.env`. Si l'utilisateur demande explicitement une tâche du module, répondre : « Ce module n'est pas actif — lancez `/modules` pour l'activer. »
- À l'activation, si le dossier du module ne contient que son `CLAUDE.md`, créer l'arborescence décrite dans ce `CLAUDE.md` (sous-dossiers + `.gitkeep`).

### Étape 6 — Récapitulatif

Afficher l'état final de tous les modules et les prochaines étapes utiles (ex. : « module `automatisations` actif — documentez vos workflows dans `10-automatisations/docs/` »).

## Modes d'échec à éviter

- **Ne pas activer un module dont les prérequis échouent** « pour voir ». L'état enregistré doit refléter la réalité.
- **Ne pas désactiver silencieusement** un module dont dépend un autre (ex. `veille` alimentée par `automatisations`) : signaler la dépendance et demander confirmation.
- **Ne jamais afficher une valeur de `.env`.** Présence uniquement.
- **Ne pas dupliquer l'état** ailleurs que dans `.setup-completed.modules`.
