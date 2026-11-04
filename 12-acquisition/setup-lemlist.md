# Connexion Lemlist (MCP)

## 1. Prérequis
- Un compte Lemlist actif ({{LEMLIST_SIGNUP_URL}}).
- Claude Code (ou tout client MCP).

## 2. Connecter le serveur MCP officiel

Documentation Lemlist : https://developer.lemlist.com/mcp/setup

Deux modes d'authentification :
- **OAuth (recommandé)** : ajoutez le serveur MCP Lemlist dans une session interactive — le navigateur s'ouvre pour autoriser l'accès au workspace. Aucun token statique à stocker : Claude Code gère l'authentification. C'est la pratique n° 1 de la hiérarchie des secrets MCP (`SECURITY.md`).
- **Clé API** : générez la clé dans Lemlist (Settings → Team → Integrations → *Generate*), puis déclarez le serveur en **portée locale**, vous-même, dans votre propre terminal (pas dans Claude Code), depuis la racine du repo. La clé est lue sans écho par `read -rs` : elle n'entre ni dans le chat ni dans l'historique du shell, et la configuration va dans `~/.claude.json`, hors du dépôt.

  ```bash
  printf 'Clé API Lemlist (saisie masquée) : '; read -rs LEMLIST_API_KEY; echo
  claude mcp add --scope local --transport http lemlist https://app.lemlist.com/mcp \
    --header "X-API-Key: $LEMLIST_API_KEY"
  unset LEMLIST_API_KEY
  ```

  Voie de repli : l'entrée `"lemlist": { "type": "http", "url": "https://app.lemlist.com/mcp", "headers": { "X-API-Key": "VOTRE_CLE_API_LEMLIST" } }` dans le `.mcp.json` local (gitignoré, jamais commité — `cp .mcp.json.example .mcp.json` s'il n'existe pas), clé en dur. Ne passez pas par `${LEMLIST_API_KEY}` + `.env` : Claude Code ne développe pas les `${VAR}` de `.mcp.json` depuis le `.env` du projet.

Vérifiez ensuite avec `/mcp` que les outils Lemlist apparaissent, puis lancez `/health-check`.

## 3. Ce que le cockpit peut faire une fois connecté
- Auditer les campagnes existantes (structure, stats par étape).
- Créer une campagne, ses séquences multicanales et ses variables de personnalisation.
- Pousser des leads (depuis une liste produite par la skill `scraping` ou un import).
- Relever les résultats pour `performance-report`.

## 4. Règles d'usage
1. **Étape 0 doctrine** : toute séquence est rédigée après chargement de `01-brand/checklist-pre-composition.md` — pas de cold email au style IA générique.
2. **Relecture humaine obligatoire** avant activation d'une campagne : le cockpit prépare, l'humain lance.
3. **Jamais d'envoi de test vers de vrais prospects** ; utilisez votre propre adresse.
4. Les listes respectent [conformite-rgpd.md](conformite-rgpd.md) : ciblage pertinent par rapport à la fonction, source des données traçable.
