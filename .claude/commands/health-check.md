---
name: health-check
description: Diagnostic continu. Vérifie .setup-completed, les placeholders, les credentials .env, les serveurs MCP réellement connectés, les modules actifs et leurs prérequis, la présence des CLAUDE.md, l'inbox 00-intel non traitée et le câblage des hooks. À lancer chaque mois ou dès qu'un truc cloche.
---

# /health-check — vérifier la santé du système

Charger d'abord la skill `copilot-setup`.

## Intention

Tout dérive : les clés API expirent, les serveurs MCP se déconnectent, les hooks se débranchent, les prérequis d'un module disparaissent. Cette commande exécute une batterie de vérifications **non destructives** et rapporte ce qui va et ce qui demande attention.

Exécutable à tout moment. Aucune écriture, aucun appel API au-delà de tests de reachability.

## Vérifications

### 1. `.setup-completed` existe et est valide

- Lire `.setup-completed`, valider contre `docs/setup-completed.schema.json`.
- Absent : setup incomplet → suggérer `/start-copilot`.
- Malformé : afficher l'erreur de validation.

### 2. Linter de placeholders

```
python3 scripts/lint-placeholders.py
```

Rapporter le code de sortie et les placeholders restants.

### 3. Credentials `.env` présents et valides

- Pour chaque outil activé dans `.setup-completed.tools.*` et chaque module actif dans `.setup-completed.modules.*`, vérifier que les variables requises sont **présentes et non vides** dans `.env` (présence uniquement — ne jamais afficher les valeurs).
- **Validité** (tests légers, lecture seule, un appel max par outil) :
  - API HTTP (Postiz, MailerLite, Notion…) : un GET de type "who am I / ping" → 200 attendu ; 401/403 = clé invalide ou expirée.
  - FTP espace client : listing du répertoire distant, jamais d'écriture.
  - GA4 / Search Console : présence du fichier pointé par `GOOGLE_APPLICATION_CREDENTIALS`.
- Signaler : `[set]` / `[unset]` / `[invalide (HTTP 401)]`.

### 4. Serveurs MCP réellement connectés

- `claude mcp list` — comparer avec `.mcp.json` et les MCP attendus par les outils configurés (ex. `magnific` si installé).
- Pour chaque serveur : distinguer **déclaré** (présent dans la config) de **connecté** (le serveur démarre / répond). Un serveur déclaré mais en échec de connexion est un 🟠.

### 5. Modules actifs et leurs prérequis

Pour chaque module `enabled: true` dans `.setup-completed.modules` :

| Module | Vérification |
|---|---|
| `video` | macOS (`uname -s` == `Darwin`) + Palmier Pro toujours installé |
| `automatisations` | `N8N_BASE_URL` set + instance joignable (GET healthz) |
| `reporting` | Au moins une source de données valide (check 3) |
| `acquisition` | n8n joignable ; `APIFY_TOKEN` set si scraping configuré |
| `veille` | `00-intel/` présent avec ses sous-dossiers |
| `publication-sociale` | `POSTIZ_API_KEY` set + API joignable |
| `espace-client` | `FTP_*` sets + listing FTP OK |

Un module actif dont un prérequis a disparu = 🟠 avec suggestion (`/modules` pour re-vérifier ou désactiver).

### 6. Présence des `CLAUDE.md`

- Vérifier qu'un `CLAUDE.md` existe : à la racine, dans chaque dossier du cœur (`01-brand` → `07-events`, `09-seo`, `02-strategy/calendar`, `00-intel`) et dans chaque dossier de module **actif** (`08-video`, `10-automatisations`, `11-reporting`, `12-acquisition`).
- Un `CLAUDE.md` manquant = 🔴 (le rôle opérera sans doctrine).

### 7. `00-intel/inbox/` non traité

- Lister les fichiers de `00-intel/inbox/` (hors `.gitkeep`).
- S'il y en a : 🟠 avec le compte et les 5 plus anciens — suggérer une session de classification (voir `00-intel/CLAUDE.md`).

### 8. Câblage des hooks

- `.claude/settings.json` : hook PostToolUse (brand-check) et hook SessionStart enregistrés.
- `.claude/hooks/brand-check-reminder.py` et `.claude/hooks/session-start.py` existent.
- Test synthétique :
  ```
  echo '{"tool_input":{"file_path":"03-social-media/linkedin/drafts/test.md"}}' | python3 .claude/hooks/brand-check-reminder.py
  python3 .claude/hooks/session-start.py < /dev/null
  ```

### 9. Fraîcheur du calendrier et du tableau d'état

- `02-strategy/calendar/calendar.md` : existe ; signaler s'il ne contient aucune entrée datée dans les 14 prochains jours (calendrier à l'abandon ?).
- Tableau tool-status du `README.md` vs `.setup-completed.tools.*` : si divergence, suggérer `/tools-setup`.

### 10. Hygiène git

- `git status --porcelain` — signaler les modifications non commitées sur les fichiers opérationnels.
- `grep -r "API_KEY\|TOKEN\|SECRET\|PASSWORD" --include="*.md" --include="*.py" .` (en excluant `.env*`, `.setup-archive/`, `docs/`, `00-intel/`) — signaler toute chaîne ressemblant à un secret en dur.
- Vérifier que `00-intel/` est bien couvert par `.gitignore` et qu'aucun fichier de contenu de `00-intel/` n'est tracké.

## Format du rapport

```
## Health Check — <ISO 8601>

| Vérification | Statut | Détail |
|---|---|---|
| .setup-completed | ✅ | Valide, version 2.0.0 |
| Placeholders | ✅ | Aucun {{*}} résiduel |
| Credentials .env | 🟠 | POSTIZ_API_KEY [unset] |
| Serveurs MCP | ✅ | 2 déclarés, 2 connectés |
| Modules actifs | 🟠 | espace-client : listing FTP en échec (hôte injoignable) |
| CLAUDE.md | ✅ | 12/12 présents |
| 00-intel/inbox | 🟠 | 3 fichiers non classés (le plus ancien : 12 jours) |
| Hooks | ✅ | PostToolUse + SessionStart câblés |
| Calendrier | ✅ | 5 entrées dans les 14 prochains jours |
| Hygiène git | ✅ | Propre, 00-intel ignoré |

### Actions
1. Renseigner POSTIZ_API_KEY dans .env (voir .env.example)
2. Vérifier l'hôte FTP — l'espace client est inaccessible
3. Classer les 3 fichiers de 00-intel/inbox/
```

## Disposition de sortie

- Tout vert : « ✅ Tous les systèmes sont opérationnels. »
- Avertissements seuls : lister les actions, le travail peut continuer.
- Blocages : expliquer l'impact de chacun et proposer la remédiation.

## Modes d'échec à éviter

- **Aucune remédiation automatique.** Cette commande est diagnostique.
- **Aucun secret affiché.** `[set]` / `[unset]` / `[invalide]` uniquement.
- **Aucun job long.** Tests de reachability seulement, jamais de synchro ni de push.
- **Aucune écriture de fichier.**
