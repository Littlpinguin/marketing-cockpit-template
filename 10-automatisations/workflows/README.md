# workflows/ — vos workflows en production, versionnés

Ce dossier reçoit **une copie JSON de vos workflows en production**, versionnée dans votre fork privé. C'est la moitié « code » de votre système d'automatisation : l'instance n8n exécute, ce dossier historise.

## Comment l'alimenter

- **Export automatique** : `../scripts/backup-workflows.sh` exporte tous les workflows via l'API n8n (à planifier en cron quotidien). Les exports bruts vont dans `../backups/` (gitignoré) ; copiez ici, sous un nom stable, la version des workflows que vous voulez versionner.
- **Export à la demande** : via l'API n8n (`GET /api/v1/workflows/<id>`), via `n8n-mcp` (demander à Claude d'exporter le workflow), ou depuis l'UI n8n (*Download*).
- **Convention de nommage** : `<domaine>-<action>-<cible>.json` en kebab-case, aligné sur le nom du workflow (ex. `intel-analyser-transcriptions.json`).

Chaque workflow versionné ici doit avoir son REX dans `../docs/` (format : `../rex-template.md`) et, s'il est non trivial, son plan dans `../plans/`.

## Fork privé vs template public

- **Dans votre fork privé** : committez vos exports tels quels (ils contiennent vos emails, IDs de documents et noms de credentials — jamais les secrets eux-mêmes, qui restent dans le vault n8n). C'est votre backup versionné.
- **Si vous contribuez un workflow au template public** : sanitisez d'abord — remplacez emails, IDs de credentials, IDs de documents et URLs d'instance par des placeholders `{{...}}`, puis vérifiez par grep (tokens `eyJ...`, emails, domaines internes) avant commit. Voir `SECURITY.md` à la racine.

## Workflows d'exemple

Le dossier `examples/` contient 4 workflows génériques et sanitisés, prêts à importer pour démarrer (error handler global, transcription → intel, veille hebdo, rapport quotidien) : voir `examples/README.md` pour les placeholders à remplacer et les credentials à recréer.
