# mcp-setup.md — brancher Claude Code sur votre instance n8n

Le `.mcp.json` à la racine du template est volontairement vide (`"mcpServers": {}`) et le format JSON n'accepte pas de commentaires : ce fichier documente donc le bloc exact à y coller pour activer le serveur [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) — la brique qui permet à Claude Code de créer, valider et déboguer les workflows directement sur l'instance.

## 1. Prérequis — variables d'environnement

Dans le `.env` à la racine du repo (jamais committé, déjà dans `.gitignore`) :

```bash
N8N_API_URL="https://{{VOTRE_INSTANCE_N8N}}/api/v1"
N8N_API_KEY="{{VOTRE_CLE_API_N8N}}"
```

La clé API se génère dans n8n : *Settings → n8n API → Create an API key*. Installation complète de l'instance : `INSTALL.md`.

## 2. Le bloc à coller dans `.mcp.json` (racine du repo)

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "${N8N_API_URL}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "WEBHOOK_SECURITY_MODE": "moderate"
      }
    }
  }
}
```

Si votre `.mcp.json` contient déjà d'autres serveurs, ajoutez seulement l'entrée `"n8n-mcp": { ... }` dans `mcpServers`.

Notes :

- **`${N8N_API_URL}` / `${N8N_API_KEY}`** référencent les variables du `.env` : le `.mcp.json` peut être committé, il ne contient aucun secret. Ne remplacez jamais ces références par des valeurs en dur.
- **`WEBHOOK_SECURITY_MODE: "moderate"`** : mode de sécurité du déclenchement de webhooks via MCP (configuration issue du système de production dont ce module est porté).
- **`LOG_LEVEL: "error"` + `DISABLE_CONSOLE_OUTPUT`** : évite le bruit dans le protocole stdio.

## 3. Vérification

1. Redémarrez Claude Code, puis `/mcp` : `n8n-mcp` doit apparaître connecté.
2. Demandez à Claude de lister vos workflows — la réponse doit venir de votre instance.

## 4. Ce que le MCP donne à Claude (et comment l'utiliser)

| Capacité | Usage dans la méthode |
|---|---|
| Documentation + recherche des nodes | Phase plan : vérifier les propriétés réelles d'un node avant de le configurer |
| `validate_node` (minimal / full), `validate_workflow` | Avant toute activation — validation multi-niveaux obligatoire (`conventions.md`) |
| CRUD workflows (création, diff, connexions) | Phase exécution : construire tâche par tâche selon le plan validé |
| Lecture des exécutions (réussies / en échec) | Débogage : diagnostiquer sur les données réelles d'exécution |

Règles d'usage — voir `conventions.md`, section « Règles critiques MCP & construction » : jamais de modification directe d'un workflow de production, jamais de confiance aux valeurs par défaut, backups avant modification, et **jamais d'affichage de credentials via MCP**.
