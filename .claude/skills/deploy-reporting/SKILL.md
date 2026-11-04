---
name: deploy-reporting
description: "Publie le dashboard de reporting de {{COMPANY_NAME}} sur l'espace client par FTP : dry-run de la liste des fichiers, confirmation explicite, puis upload lftp ou curl. À lancer à la main après performance-report, une fois l'analyse du mois validée."
disable-model-invocation: true
---

# deploy-reporting — mise en ligne du dashboard sur l'espace client

Étape séparée de `performance-report` : l'upload FTP écrit sur le serveur du client, c'est une action externe. Elle ne part que sur demande explicite de l'utilisateur (`/deploy-reporting`), jamais depuis une autre skill ni depuis un run sans surveillance. Le mécanisme complet (arborescence distante, credentials, premier déploiement) est décrit dans `11-reporting/deploy/README.md` : le lire avant d'agir.

## Prérequis (arrêt si l'un manque)

- Le snapshot `02-strategy/performance/YYYY-MM/data.json` du mois existe et son analyse a été **validée par l'utilisateur** (gate de `11-reporting/CLAUDE.md`).
- Le dashboard a été prévisualisé en local (`11-reporting/deploy/README.md`, étape 1).
- `11-reporting/dashboard/template.html` ne contient plus de placeholder `{{…}}` (sinon, les remplir avant le premier déploiement).
- Les clés `CLIENT_FTP_HOST`, `CLIENT_FTP_USER`, `CLIENT_FTP_PASSWORD`, `CLIENT_FTP_BASE` sont définies dans `.env` (configurées par `/tools-setup`). Vérifier leur présence seulement (`définie` / `non définie`), ne jamais afficher leur valeur. Clé absente : s'arrêter et renvoyer vers `/tools-setup`.

## Étape 1 — Préparer les fichiers

Copier le snapshot validé vers `11-reporting/dashboard/data/YYYY-MM.json` et ajouter le mois à `11-reporting/dashboard/data/index.json` (champ `mois`, trié). Un mois déjà présent dans `index.json` n'est pas ajouté une seconde fois.

## Étape 2 — Dry-run d'abord

Sans rien envoyer, afficher :
- la liste des fichiers qui seront transférés (en général `data/YYYY-MM.json`, `data/index.json` et, s'il a changé, `template.html` publié sous `dashboard.html`) ;
- la destination : hôte et chemin distant (`$CLIENT_FTP_BASE/dashboard/`), jamais le mot de passe.

Pour obtenir la liste exacte des différences côté serveur, `lftp` sait simuler le miroir sans écrire :

```bash
set -a; source .env; set +a
lftp -u "$CLIENT_FTP_USER","$CLIENT_FTP_PASSWORD" "ftp://$CLIENT_FTP_HOST" -e "
  set ftp:ssl-force true; set ssl:verify-certificate true;
  mirror -R --dry-run --only-newer 11-reporting/dashboard/data $CLIENT_FTP_BASE/dashboard/data;
  bye
"
```

## Étape 3 — Confirmation explicite

Attendre un accord explicite de l'utilisateur sur cette liste et cette destination avant l'upload réel (`SECURITY.md`, section « Dry-run avant tout push en production »). Un accord donné pour un autre mois ou une autre liste de fichiers ne vaut pas pour celui-ci.

## Étape 4 — Upload

Commande de référence de `11-reporting/deploy/README.md` (lftp, FTPS imposé) :

```bash
set -a; source .env; set +a
lftp -u "$CLIENT_FTP_USER","$CLIENT_FTP_PASSWORD" "ftp://$CLIENT_FTP_HOST" -e "
  set ftp:ssl-force true; set ssl:verify-certificate true;
  mirror -R --verbose --only-newer \
    11-reporting/dashboard/data \
    $CLIENT_FTP_BASE/dashboard/data;
  put -O $CLIENT_FTP_BASE/dashboard 11-reporting/dashboard/template.html -o dashboard.html;
  bye
"
```

- Si l'hébergeur propose SFTP, remplacer l'URL par `sftp://$CLIENT_FTP_HOST`.
- **Pas de `--delete`** sur `data/` : les mois précédents restent en ligne.
- Sans `lftp`, l'alternative `curl --ssl-reqd -T` fichier par fichier est décrite dans le même README.

## Étape 5 — Après l'upload

Donner l'URL de l'espace client et proposer une vérification visuelle : navigation privée, page de code, dashboard aux couleurs de la marque, navigation entre les mois. Le code d'accès n'apparaît jamais dans un message.

## Ce que cette skill ne fait PAS

- ❌ Collecter, analyser ou régénérer le dashboard (→ `performance-report`)
- ❌ Le premier déploiement de l'espace client (`protect.php`, `config.php`, `robots.txt`) : checklist manuelle de `11-reporting/deploy/README.md`
- ❌ Notifier le client par email : c'est un envoi de message, sur demande séparée
- ❌ Tourner sans surveillance : la voie automatisée (n8n, `11-reporting/automation.md`) déploie par son propre nœud FTP, après sa gate de validation humaine
