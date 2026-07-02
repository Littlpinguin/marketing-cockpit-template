# INSTALL — n8n self-hosted + MCP n8n pour Claude Code

Ce guide couvre : l'installation de n8n sur un VPS (Docker + HTTPS + authentification), la mise en place de l'error workflow global, la configuration du serveur MCP `n8n-mcp` côté Claude Code, et les bonnes pratiques de sécurité.

> **Alternative sans VPS** : créez un compte sur [n8n.io](https://n8n.io) (n8n Cloud), générez une clé API, et passez directement à l'étape 5. Tout le reste du module fonctionne à l'identique.

---

## 1. Prérequis

- Un VPS Linux (Ubuntu 22.04+ recommandé), 2 Go de RAM minimum — offres d'entrée de gamme chez Hostinger, Contabo, OVH, Scaleway, Hetzner...
- Un nom de domaine (ou sous-domaine) pointant vers l'IP du VPS, ex. `n8n.{{VOTRE_DOMAINE}}`
- Un accès SSH avec un utilisateur non-root sudoer

> **Astuce Hostinger** : leurs VPS proposent un template « n8n » pré-installé (Docker + Traefik + HTTPS déjà configurés). Si vous prenez cette option, vérifiez quand même les étapes 3 (authentification), 4 (error workflow) et 6 (sécurité).

## 2. Installer Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Reconnectez-vous pour que le groupe soit pris en compte
```

## 3. Lancer n8n avec HTTPS et authentification

Créez un dossier de travail et un `docker-compose.yml` :

```bash
mkdir -p ~/n8n && cd ~/n8n
```

```yaml
# docker-compose.yml
services:
  traefik:
    image: traefik:latest
    restart: unless-stopped
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email={{VOTRE_EMAIL_ADMIN}}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./letsencrypt:/letsencrypt
      - /var/run/docker.sock:/var/run/docker.sock:ro

  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: unless-stopped
    environment:
      - N8N_HOST=n8n.{{VOTRE_DOMAINE}}
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.{{VOTRE_DOMAINE}}/
      - GENERIC_TIMEZONE=Europe/Paris
      - N8N_ENCRYPTION_KEY={{CLE_CHIFFREMENT_GENEREE}}   # openssl rand -hex 32 — SAUVEGARDEZ-LA
      - N8N_DIAGNOSTICS_ENABLED=false
    volumes:
      - n8n_data:/home/node/.n8n
      - ./intel-drop:/data/intel-drop          # dossier d'échange pour meeting-transcript-to-intel
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.{{VOTRE_DOMAINE}}`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls.certresolver=letsencrypt"
      - "traefik.http.services.n8n.loadbalancer.server.port=5678"

volumes:
  n8n_data:
```

```bash
docker compose up -d
```

Points importants :

- **`N8N_ENCRYPTION_KEY`** chiffre le vault de credentials. Générez-la (`openssl rand -hex 32`), stockez-la dans un gestionnaire de mots de passe. Sans elle, vos credentials sont irrécupérables en cas de restauration.
- **Authentification** : au premier accès à `https://n8n.{{VOTRE_DOMAINE}}`, n8n vous fait créer le compte propriétaire (email + mot de passe fort). N'exposez jamais une instance sans compte configuré. Activez la 2FA dans *Settings → Personal*.
- **Webhooks** : le mode HTTPS est indispensable pour recevoir les webhooks des outils externes (transcription, CRM, outreach).

## 4. Error workflow global (à faire avant tout le reste)

1. Dans n8n : *Workflows → Import from file* → `workflows/error-handler.json`.
2. Remplacez les placeholders (voir `workflows/README.md`), créez le credential SMTP dans le vault, activez le workflow.
3. Notez son ID (visible dans l'URL : `/workflow/<ID>`).
4. Dans **chaque** workflow que vous créerez ensuite : *Options → Settings → Error workflow* → sélectionnez ce workflow. Dans les JSON du template, c'est le placeholder `{{ERROR_WORKFLOW_ID}}`.

Résultat : toute erreur d'exécution, sur n'importe quel workflow, déclenche un email détaillé (workflow, node en erreur, message, lien vers l'exécution).

## 5. Clé API n8n + variables d'environnement du copilot

1. Dans n8n : *Settings → n8n API → Create an API key*.
2. Dans le `.env` à la racine de ce repo (jamais committé) :

```bash
N8N_API_URL="https://n8n.{{VOTRE_DOMAINE}}/api/v1"
N8N_API_KEY="{{VOTRE_CLE_API_N8N}}"
```

## 6. Configurer le MCP n8n côté Claude Code

Le serveur [n8n-mcp](https://github.com/czlonkowski/n8n-mcp) donne à Claude Code un accès outillé à votre instance : documentation des nodes, validation de configuration, CRUD des workflows, lecture des exécutions.

Ajoutez (ou complétez) `.mcp.json` à la racine du repo :

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
        "N8N_API_KEY": "${N8N_API_KEY}"
      }
    }
  }
}
```

- La syntaxe `${N8N_API_URL}` fait référence aux variables du `.env` : **le `.mcp.json` peut être committé, il ne contient aucun secret**.
- Redémarrez Claude Code, puis vérifiez avec `/mcp` que `n8n-mcp` est connecté.
- Usage recommandé : demander à Claude de **valider** un workflow (`validate_node` puis `validate_workflow`) avant toute activation — voir `conventions.md`.

## 7. Sécurité — règles à appliquer systématiquement

1. **Credentials dans le vault n8n chiffré, UNIQUEMENT.** Jamais de clé API, token OAuth, mot de passe SMTP en dur dans un node, une expression, un Code node ou un JSON exporté.
2. **Purger avant de committer.** Un export de workflow n8n embarque les noms et IDs de credentials, parfois des emails et des IDs de documents. Avant tout commit dans `workflows/` : remplacer par des placeholders `{{...}}` et passer un grep de contrôle (pattern de tokens `eyJ...`, emails, URLs d'instance).
3. **Webhooks exposés** : chemin non devinable, et si l'émetteur le permet, header d'authentification vérifié dans un node de validation en entrée.
4. **Moindre privilège** : scopes OAuth minimaux, une clé API par usage, révocation facile.
5. **Ne jamais afficher les credentials via MCP** : l'API n8n ne renvoie pas les secrets, ne tentez pas de les contourner via des nodes de debug.
6. **Mises à jour** : `docker compose pull && docker compose up -d` régulièrement (failles corrigées fréquemment).
7. **Backups** : `scripts/backup-workflows.sh` en cron quotidien + snapshot du volume `n8n_data` (qui contient la base SQLite et le vault). Testez une restauration au moins une fois.

## 8. Vérification finale

- [ ] `https://n8n.{{VOTRE_DOMAINE}}` répond en HTTPS avec certificat valide
- [ ] Compte propriétaire + 2FA activés
- [ ] Error workflow importé, activé, testé (provoquez une erreur volontaire)
- [ ] `N8N_API_URL` / `N8N_API_KEY` dans `.env`, `.env` bien dans `.gitignore`
- [ ] `n8n-mcp` visible dans `/mcp` de Claude Code
- [ ] Backup quotidien planifié et testé
