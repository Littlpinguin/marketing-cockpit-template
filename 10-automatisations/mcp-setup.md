# mcp-setup.md — brancher Claude Code sur votre instance n8n

Le `.mcp.json` à la racine du repo est **local et non versionné** (gitignoré) : c'est lui qui porte les vraies valeurs de connexion. Le template versionne uniquement `.mcp.json.example` (structure + placeholders). Ce guide couvre l'activation du serveur [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) — la brique qui permet à Claude Code de créer, valider et déboguer les workflows directement sur l'instance.

## 1. Prérequis — clé API et `.env` (pour les scripts)

La clé API se génère dans n8n : *Settings → n8n API → Create an API key*. Installation complète de l'instance : `INSTALL.md`.

Dans le `.env` à la racine du repo (jamais committé, déjà dans `.gitignore`) :

```bash
N8N_API_URL="https://{{VOTRE_INSTANCE_N8N}}/api/v1"
N8N_API_KEY="{{VOTRE_CLE_API_N8N}}"
```

Ces variables `.env` servent aux **scripts** (ex. `scripts/backup-workflows.sh`, qui charge le `.env` lui-même). Elles ne suffisent **pas** pour le serveur MCP — voir la note technique ci-dessous.

## 2. Le `.mcp.json` local (racine du repo)

Au premier setup, copiez l'exemple versionné puis renseignez vos vraies valeurs :

```bash
cp .mcp.json.example .mcp.json   # .mcp.json est gitignoré — il ne sera jamais commité
```

Contenu attendu, avec vos **valeurs réelles en dur** (URL et clé API) :

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
        "N8N_API_URL": "https://VOTRE_INSTANCE_N8N/api/v1",
        "N8N_API_KEY": "VOTRE_CLE_API_N8N",
        "WEBHOOK_SECURITY_MODE": "moderate"
      }
    }
  }
}
```

Si votre `.mcp.json` contient déjà d'autres serveurs, ajoutez seulement l'entrée `"n8n-mcp": { ... }` dans `mcpServers`.

Notes :

- **⚠️ Note technique — pourquoi pas `${N8N_API_KEY}` + `.env` ?** Claude Code ne développe les références `${VAR}` de `.mcp.json` que depuis l'**environnement du processus**, jamais depuis le `.env` du projet. Le pattern « `${N8N_API_KEY}` dans `.mcp.json` + valeur dans `.env` » produit une connexion cassée (401). D'où le pattern du template : valeurs réelles dans le `.mcp.json` local non versionné. La hiérarchie complète des pratiques (OAuth quand disponible, 1Password `op run`, etc.) est dans `SECURITY.md`.
- **Alternative avancée** si vous tenez aux références `${VAR}` : exportez les variables dans l'environnement qui lance Claude Code (profil shell ou launchd). Déconseillé — le secret est en clair sur disque et visible de tous les processus (voir `SECURITY.md`).
- **`WEBHOOK_SECURITY_MODE: "moderate"`** : mode de sécurité du déclenchement de webhooks via MCP (configuration issue du système de production dont ce module est porté).
- **`LOG_LEVEL: "error"` + `DISABLE_CONSOLE_OUTPUT`** : évite le bruit dans le protocole stdio.

## 3. Vérification

1. Redémarrez Claude Code, puis `/mcp` : `n8n-mcp` doit apparaître connecté.
2. `git check-ignore .mcp.json` doit répondre `.mcp.json` (le fichier est bien ignoré — jamais commité).
3. Demandez à Claude de lister vos workflows — la réponse doit venir de votre instance.

## 4. Ce que le MCP donne à Claude (et comment l'utiliser)

| Capacité | Usage dans la méthode |
|---|---|
| Documentation + recherche des nodes | Phase plan : vérifier les propriétés réelles d'un node avant de le configurer |
| `validate_node` (minimal / full), `validate_workflow` | Avant toute activation — validation multi-niveaux obligatoire (`conventions.md`) |
| CRUD workflows (création, diff, connexions) | Phase exécution : construire tâche par tâche selon le plan validé |
| Lecture des exécutions (réussies / en échec) | Débogage : diagnostiquer sur les données réelles d'exécution |

Règles d'usage — voir `conventions.md`, section « Règles critiques MCP & construction » : jamais de modification directe d'un workflow de production, jamais de confiance aux valeurs par défaut, backups avant modification, et **jamais d'affichage de credentials via MCP**.
