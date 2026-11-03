# mcp-setup.md — brancher Claude Code sur votre instance n8n

Ce guide couvre l'activation du serveur [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) — la brique qui permet à Claude Code de créer, valider et déboguer les workflows directement sur l'instance. Voie recommandée : déclarer le serveur en **portée locale** de Claude Code (`claude mcp add --scope local`), que Claude Code range dans `~/.claude.json`, hors du dépôt. Voie de repli : le `.mcp.json` à la racine du repo, **local et non versionné** (gitignoré), copié depuis `.mcp.json.example` (structure + placeholders, seul fichier versionné).

## 1. Prérequis — clé API et `.env` (pour les scripts)

La clé API se génère dans n8n : *Settings → n8n API → Create an API key*. Installation complète de l'instance : `INSTALL.md`.

Dans le `.env` à la racine du repo (jamais committé, déjà dans `.gitignore`) :

```bash
N8N_API_URL="https://{{VOTRE_INSTANCE_N8N}}/api/v1"
N8N_API_KEY="{{VOTRE_CLE_API_N8N}}"
```

Ces variables `.env` servent aux **scripts** (ex. `scripts/backup-workflows.sh`, qui charge le `.env` lui-même). Elles ne suffisent **pas** pour le serveur MCP — voir la note technique de l'étape 3.

## 2. Déclarer le serveur en portée locale (recommandé)

Cette commande se lance **par vous, dans votre propre terminal**, depuis la racine du repo : la portée locale est rattachée au dossier où la commande est lancée, celui où vous ouvrez Claude Code. Ni dans une conversation Claude Code, ni avec son préfixe `!` (la sortie entrerait dans la conversation) : la clé ne passe jamais par le chat ni par une commande que Claude lance. Remplacez `VOTRE_INSTANCE_N8N` par l'adresse de votre instance ; la clé, elle, est lue sans écho par `read -rs`, et l'historique du shell ne garde que le texte `$N8N_API_KEY`, jamais sa valeur (zsh comme bash) :

```bash
printf 'Clé API n8n (saisie masquée) : '; read -rs N8N_API_KEY; echo
claude mcp add --scope local --transport stdio n8n-mcp \
  -e MCP_MODE=stdio -e LOG_LEVEL=error -e DISABLE_CONSOLE_OUTPUT=true \
  -e WEBHOOK_SECURITY_MODE=moderate \
  -e N8N_API_URL=https://VOTRE_INSTANCE_N8N/api/v1 \
  -e "N8N_API_KEY=$N8N_API_KEY" \
  -- npx n8n-mcp@2.94.3
unset N8N_API_KEY
```

- Les options de Claude Code (`--scope`, `--transport`, `-e`) précèdent `--` ; ce qui suit `--` est la commande du serveur, transmise telle quelle.
- `claude mcp add` enregistre sans vérifier la clé : une erreur ne se voit qu'à la connexion (étape 5).
- Changer la clé ou la version : `claude mcp remove --scope local n8n-mcp`, puis relancer le bloc.
- La clé est en clair dans `~/.claude.json` (hors du dépôt, chiffrement disque type FileVault recommandé). Claude ne lit pas ce fichier et ne lance pas `claude mcp get n8n-mcp`, qui affiche les variables du serveur : il vérifie par `claude mcp list` (nom, commande, état).

## 3. Voie de repli — le `.mcp.json` local (racine du repo)

Si vous préférez un fichier dans le projet, copiez l'exemple versionné puis renseignez vos vraies valeurs :

```bash
cp .mcp.json.example .mcp.json   # .mcp.json est gitignoré — il ne sera jamais commité
```

Contenu attendu, avec vos **valeurs réelles en dur** (URL et clé API) :

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp@2.94.3"],
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

Si votre `.mcp.json` contient déjà d'autres serveurs, ajoutez seulement l'entrée `"n8n-mcp": { ... }` dans `mcpServers`. Un même nom déclaré en portée locale et dans `.mcp.json` : Claude Code prend l'entrée de la portée locale, en entier. Après un passage à la portée locale, retirez l'entrée de `.mcp.json` pour que la clé ne reste pas dans le dossier du projet.

Notes :

- **⚠️ Note technique — pourquoi pas `${N8N_API_KEY}` + `.env` ?** Claude Code ne développe les références `${VAR}` de `.mcp.json` que depuis l'**environnement du processus**, jamais depuis le `.env` du projet. Le pattern « `${N8N_API_KEY}` dans `.mcp.json` + valeur dans `.env` » produit une connexion cassée (401). D'où les deux voies du template : la portée locale (étape 2), ou les valeurs réelles dans le `.mcp.json` local non versionné. La hiérarchie complète des pratiques (OAuth quand disponible, 1Password `op run`, etc.) est dans `SECURITY.md`.
- **Alternative avancée** si vous tenez aux références `${VAR}` : exportez les variables dans l'environnement qui lance Claude Code (profil shell ou launchd). Déconseillé — le secret est en clair sur disque et visible de tous les processus (voir `SECURITY.md`).
- **`WEBHOOK_SECURITY_MODE: "moderate"`** (les deux voies) : mode de sécurité du déclenchement de webhooks via MCP (configuration issue du système de production dont ce module est porté).
- **`LOG_LEVEL: "error"` + `DISABLE_CONSOLE_OUTPUT`** (les deux voies) : évite le bruit dans le protocole stdio.

## 4. Version épinglée du serveur

`npx` lance une version fixe, **`n8n-mcp@2.94.3`** (publiée sur npm le 19 octobre 2026), et non la dernière publiée : sans numéro, chaque démarrage exécuterait la version du jour, votre clé API dans son environnement. Le paquet npm déclare pour dépôt source `github.com/czlonkowski/n8n-mcp`, celui que cite ce guide. Pour monter de version :

1. Lire le [changelog amont](https://github.com/czlonkowski/n8n-mcp/blob/main/CHANGELOG.md) (et les [releases](https://github.com/czlonkowski/n8n-mcp/releases)) entre la version en place et la cible. Choisir une version publiée depuis au moins 14 jours : `npm view n8n-mcp time --json` donne les dates sans rien installer.
2. Changer le numéro : en portée locale, `claude mcp remove --scope local n8n-mcp` puis le bloc de l'étape 2 avec le nouveau numéro ; en repli, dans `args` du `.mcp.json`.
3. Redémarrer Claude Code et refaire la vérification de l'étape 5.

Dans le template, le numéro figure aussi dans `.mcp.json.example`, `INSTALL.md` et `SECURITY.md` : `git grep -n 'n8n-mcp@'` les retrouve tous.

## 5. Vérification

1. Redémarrez Claude Code, puis `/mcp` : `n8n-mcp` doit apparaître connecté.
2. Voie de repli seulement : `git check-ignore .mcp.json` doit répondre `.mcp.json` (le fichier est bien ignoré — jamais commité).
3. Demandez à Claude de lister vos workflows — la réponse doit venir de votre instance.

## 6. Ce que le MCP donne à Claude (et comment l'utiliser)

| Capacité | Usage dans la méthode |
|---|---|
| Documentation + recherche des nodes | Phase plan : vérifier les propriétés réelles d'un node avant de le configurer |
| `validate_node` (minimal / full), `validate_workflow` | Avant toute activation — validation multi-niveaux obligatoire (`conventions.md`) |
| CRUD workflows (création, diff, connexions) | Phase exécution : construire tâche par tâche selon le plan validé |
| Lecture des exécutions (réussies / en échec) | Débogage : diagnostiquer sur les données réelles d'exécution |

Règles d'usage — voir `conventions.md`, section « Règles critiques MCP & construction » : jamais de modification directe d'un workflow de production, jamais de confiance aux valeurs par défaut, backups avant modification, et **jamais d'affichage de credentials via MCP**.
