# Connexion Lemlist (MCP)

## 1. Prérequis
- Un compte Lemlist actif ({{LEMLIST_SIGNUP_URL}}).
- Claude Code (ou tout client MCP).

## 2. Connecter le serveur MCP officiel

Documentation Lemlist : https://developer.lemlist.com/mcp/setup

Deux modes d'authentification :
- **OAuth (recommandé)** : ajoutez le serveur MCP Lemlist dans une session interactive — le navigateur s'ouvre pour autoriser l'accès au workspace. Aucun token statique à stocker : Claude Code gère l'authentification. C'est la pratique n° 1 de la hiérarchie des secrets MCP (`SECURITY.md`).
- **Clé API** : générez la clé dans Lemlist (Settings → Integrations → API) et mettez-la **directement dans le `.mcp.json` local** (gitignoré, jamais commité — `cp .mcp.json.example .mcp.json` s'il n'existe pas). Ne passez pas par `${LEMLIST_API_KEY}` + `.env` : Claude Code ne développe pas les `${VAR}` de `.mcp.json` depuis le `.env` du projet.

Vérifiez ensuite avec `/mcp` que les outils Lemlist apparaissent, puis lancez `/health-check`.

## 3. Ce que le copilot peut faire une fois connecté
- Auditer les campagnes existantes (structure, stats par étape).
- Créer une campagne, ses séquences multicanales et ses variables de personnalisation.
- Pousser des leads (depuis une liste produite par la skill `scraping` ou un import).
- Relever les résultats pour `performance-report`.

## 4. Règles d'usage
1. **Étape 0 doctrine** : toute séquence est rédigée après chargement de `01-brand/checklist-pre-composition.md` — pas de cold email au style IA générique.
2. **Relecture humaine obligatoire** avant activation d'une campagne : le copilot prépare, l'humain lance.
3. **Jamais d'envoi de test vers de vrais prospects** ; utilisez votre propre adresse.
4. Les listes respectent [conformite-rgpd.md](conformite-rgpd.md) : ciblage pertinent par rapport à la fonction, source des données traçable.
