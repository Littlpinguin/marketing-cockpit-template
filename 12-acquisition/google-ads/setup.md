# Connexion Google Ads (serveur MCP mcp-google-ads)

Serveur retenu : [FGRibreau/mcp-google-ads](https://github.com/FGRibreau/mcp-google-ads) — serveur MCP en **Rust** (licence MIT, Google Ads API v23) qui expose ~47 outils : 17 en lecture (`list_accounts`, `get_campaign_performance`, `get_keyword_performance`, `get_search_terms`, `run_gaql`, `list_recommendations`, `get_conversion_actions`…) et 30 en écriture (création/modification de campagnes, mots-clés, annonces, extensions…). Il embarque des garde-fous natifs : mode lecture seule, dry-run par défaut, confirmation en deux étapes, plafond budgétaire, journal d'audit des mutations.

> **Mode conseil du copilot** : on le configure en **lecture seule**. Les 30 outils d'écriture ne servent qu'après validation humaine explicite, mutation par mutation (voir `README.md`).

## 1. Prérequis

1. **Un compte Google Ads actif** (idéalement un accès MCC si vous gérez plusieurs comptes).
2. **Un developer token Google Ads API** : Google Ads → Outils → Centre API (nécessite un compte manager). Un token en accès « test » suffit pour un compte de test ; l'accès « basic » (validation Google, quelques jours) est requis pour lire un compte de production.
3. **Un client OAuth Google Cloud** : dans [Google Cloud Console](https://console.cloud.google.com), créer un projet, activer l'API Google Ads, puis créer un identifiant OAuth 2.0 de type « Desktop app » et télécharger le `credentials.json`.
4. **La toolchain Rust** (`cargo`) : ce serveur se compile, il ne s'installe pas via npm/uvx — https://rustup.rs.

## 2. Compilation et génération du token OAuth

```bash
git clone https://github.com/FGRibreau/mcp-google-ads.git
cd mcp-google-ads
cargo build --release            # binaire : target/release/mcp-google-ads

mkdir -p ~/.mcp-google-ads
cp /chemin/vers/credentials.json ~/.mcp-google-ads/credentials.json
./scripts/generate_token.sh ~/.mcp-google-ads/credentials.json   # ouvre le navigateur, écrit token.json
```

## 3. Où vivent les credentials — jamais dans un fichier tracké

- Le **developer token et les customer IDs** vont dans le `.mcp.json` **local et non versionné** (étape 4) — c'est le serveur MCP qui les consomme, et le `.mcp.json` est gitignoré (cf. `SECURITY.md`).
- Les **fichiers OAuth** restent hors repo (`~/.mcp-google-ads/credentials.json` et `token.json` — chemins par défaut du serveur).

## 4. Déclarer le serveur MCP

Dans le `.mcp.json` local à la racine du repo (`cp .mcp.json.example .mcp.json` s'il n'existe pas encore), avec vos **valeurs réelles** :

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "/chemin/absolu/vers/target/release/mcp-google-ads",
      "env": {
        "GOOGLE_ADS_DEVELOPER_TOKEN": "VOTRE_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID": "123-456-7890",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID": "ID_DU_COMPTE_MCC_SI_APPLICABLE",
        "GOOGLE_ADS_READ_ONLY": "true",
        "GOOGLE_ADS_REQUIRE_DRY_RUN": "true"
      },
      "description": "Google Ads en mode conseil (lecture seule). Passer GOOGLE_ADS_READ_ONLY à false uniquement pour appliquer un plan validé par l'humain."
    }
  }
}
```

> ⚠️ N'utilisez **pas** de références `${VAR}` en pensant qu'elles seront lues depuis le `.env` du projet : Claude Code ne développe les `${VAR}` de `.mcp.json` que depuis l'environnement du processus. Le `.mcp.json` local n'est jamais commité — c'est lui qui porte les vraies valeurs (hiérarchie complète des pratiques : `SECURITY.md`).

Garde-fous supplémentaires du serveur, si vous ouvrez un jour l'écriture : `GOOGLE_ADS_MAX_DAILY_BUDGET` (plafond de budget quotidien, défaut 50.0), `GOOGLE_ADS_MAX_BID_INCREASE_PCT` (défaut 100), `GOOGLE_ADS_AUDIT_LOG` (journal des mutations, défaut `~/.mcp-google-ads/audit.log`). Les entités créées le sont en statut PAUSED.

## 5. Vérifier

1. `/mcp` : le serveur `google-ads` apparaît avec ses outils.
2. Demander un `health_check` puis un `list_accounts` : les comptes attendus remontent.
3. Lancer `/health-check` pour intégrer la vérification au contrôle mensuel du copilot.

## 6. Règles d'usage

1. **Lecture seule par défaut** : `GOOGLE_ADS_READ_ONLY=true` tant qu'aucun plan validé n'est en cours d'application.
2. **Aucune mutation sans validation humaine explicite** — règle dure du `README.md`, qui s'ajoute aux garde-fous du serveur.
3. **Aucun secret dans un fichier tracké** : token et customer IDs réels vivent dans le `.mcp.json` local (gitignoré), les fichiers OAuth dans `~/.mcp-google-ads/`.
4. Ce repo **ne vendorise pas** le serveur : c'est une connexion MCP. Épingler une version taguée (ex. v0.6.0) lors du `git clone` et relire le changelog avant toute montée de version.
