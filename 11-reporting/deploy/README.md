# Déploiement FTP de l'espace client

Le dashboard (et les présentations partagées) se déploient sur l'hébergement mutualisé du client par **FTP/SFTP**, dans un unique dossier protégé : l'**espace client**. Même mécanisme pour tout ce qu'on partage — un `mirror` par sous-dossier.

## Arborescence cible sur le serveur

```
www/                                  ← racine web du client
└── espace-client/                    ← protégé (voir ../acces/README.md)
    ├── config.php                    ← code d'accès — créé À LA MAIN, jamais déployé ni commité
    ├── protect.php                   ← depuis 11-reporting/acces/protect.php.example
    ├── index.php                     ← garde + redirection vers dashboard/
    ├── dashboard/
    │   ├── index.php                 ← garde + readfile('dashboard.html')
    │   ├── dashboard.html            ← 11-reporting/dashboard/template.html (placeholders remplis)
    │   └── data/
    │       ├── index.json
    │       └── YYYY-MM.json          ← copiés depuis 02-strategy/performance/YYYY-MM/data.json
    └── presentations/                ← decks HTML (06-graphic-design/presentations/decks/)
```

## Credentials — dans `.env`, jamais commités

Ajoutez au `.env` du repo client (le `.env` est dans `.gitignore` ; documentez les clés dans `.env.example`) :

```bash
# --- Espace client : déploiement FTP ---
CLIENT_FTP_HOST="ftp.{{COMPANY_DOMAIN}}"
CLIENT_FTP_USER="{{FTP_USER}}"
CLIENT_FTP_PASSWORD=""                     # jamais en clair dans un commit ni un chat
CLIENT_FTP_BASE="/www/espace-client"       # chemin distant de l'espace client
```

Règles `SECURITY.md` applicables : jamais de secret dans un message ou un commit ; **confirmation humaine explicite avant tout push en production** ; préférez SFTP ou FTPS si l'hébergeur le propose (le FTP nu transmet le mot de passe en clair).

## Étape 1 — Préparer les fichiers à publier

```bash
cd 11-reporting/dashboard

# 1. Copier le snapshot du mois validé depuis la source
cp ../../02-strategy/performance/2026-06/data.json data/2026-06.json

# 2. Ajouter le mois à data/index.json (champ "mois", trié)
# 3. Vérifier en local avant tout envoi :
python3 -m http.server 5180   # → http://localhost:5180/template.html
```

## Étape 2 — Déployer avec lftp (recommandé)

`lftp` gère le miroir incrémental (n'envoie que ce qui a changé) : `brew install lftp` / `apt install lftp`.

```bash
set -a; source .env; set +a

# Dashboard : template + données
lftp -u "$CLIENT_FTP_USER","$CLIENT_FTP_PASSWORD" "ftp://$CLIENT_FTP_HOST" -e "
  set ftp:ssl-force true; set ssl:verify-certificate true;
  mirror -R --verbose --only-newer \
    11-reporting/dashboard/data \
    $CLIENT_FTP_BASE/dashboard/data;
  put -O $CLIENT_FTP_BASE/dashboard 11-reporting/dashboard/template.html -o dashboard.html;
  bye
"
```

Notes :

- `set ftp:ssl-force true` impose FTPS ; si l'hébergeur propose SFTP, remplacez l'URL par `sftp://$CLIENT_FTP_HOST`.
- **Pas de `--delete`** sur `data/` : les snapshots des mois précédents doivent rester en ligne.
- Le `template.html` déployé doit avoir ses placeholders `{{…}}` déjà remplis (fait une fois par `/start-copilot` ; sinon remplissez-les à la main avant le premier déploiement).
- Même commande pour les présentations : `mirror -R --only-newer 06-graphic-design/presentations/decks $CLIENT_FTP_BASE/presentations`.

## Alternative — curl (un fichier à la fois, disponible partout)

Pour la mise à jour mensuelle courante (2 fichiers), `curl` suffit :

```bash
set -a; source .env; set +a

curl --ssl-reqd -T 11-reporting/dashboard/data/2026-06.json \
  "ftp://$CLIENT_FTP_HOST$CLIENT_FTP_BASE/dashboard/data/" \
  --user "$CLIENT_FTP_USER:$CLIENT_FTP_PASSWORD"

curl --ssl-reqd -T 11-reporting/dashboard/data/index.json \
  "ftp://$CLIENT_FTP_HOST$CLIENT_FTP_BASE/dashboard/data/" \
  --user "$CLIENT_FTP_USER:$CLIENT_FTP_PASSWORD"
```

## Premier déploiement (checklist une fois par client)

1. Créer `espace-client/` sur le serveur, déployer `protect.php`, `index.php`, les `index.php` de garde de `dashboard/` et `presentations/`.
2. Créer `config.php` **directement sur le serveur** (gestionnaire de fichiers ou SFTP) avec le code d'accès et le sel — jamais via le repo.
3. Déployer `dashboard.html` + `data/`.
4. Ajouter `Disallow: /espace-client/` au `robots.txt` du site.
5. Tester : URL en navigation privée → page de code → code correct → dashboard aux couleurs de la marque → navigation entre mois.
6. Transmettre lien et code au client par deux canaux séparés.

## Mise à jour mensuelle (routine)

1. Snapshot validé dans `02-strategy/performance/YYYY-MM/` (analyse comprise).
2. Copie vers `dashboard/data/` + mise à jour d'`index.json`.
3. Vérification locale, confirmation humaine, puis push (lftp ou curl).
4. Email de notification au client (court : « votre reporting est en ligne » + lien).

Automatisation complète de cette routine : voir `../automation.md` (n8n + module `10-automatisations/`).
