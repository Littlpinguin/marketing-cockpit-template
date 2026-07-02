# Code d'accès de l'espace client

L'espace client (`espace-client/` sur le site du client) est protégé par un **code d'accès unique** : le client saisit le code une fois, un cookie est posé, et il accède au dashboard et aux présentations pendant 30 jours.

## Honnêteté d'abord : c'est une protection légère

Ce mécanisme **éloigne les curieux, les moteurs de recherche et les liens partagés par erreur**. Il ne résiste pas à un attaquant déterminé (pas de comptes individuels, pas de limitation de tentatives côté infra, un seul code partagé). C'est un niveau de protection **adapté à du reporting marketing** — trafic, posts, taux d'ouverture — c'est-à-dire des données peu sensibles.

**Ne mettez jamais derrière ce système** : données personnelles de clients finaux, données financières détaillées, données de santé, contrats. Pour cela, il faut une vraie authentification (comptes + HTTPS + hébergement adapté), hors du périmètre de ce module.

Prérequis minimal non négociable : **HTTPS actif** sur le domaine (Let's Encrypt est disponible sur la quasi-totalité des mutualisés).

## Deux mécanismes au choix

### Option A — Garde PHP + cookie (recommandée : page de saisie aux couleurs de la marque)

Fonctionne sur tout hébergement mutualisé avec PHP (OVH, o2switch, Ionos…). C'est le mécanisme fourni dans `protect.php.example`.

Principe :

1. `protect.php` est inclus en tête de chaque point d'entrée de l'espace client.
2. Pas de cookie valide → affichage d'une page de saisie du code (stylée avec les tokens de marque) et arrêt.
3. Code correct soumis → cookie signé (hash du code + sel), valable 30 jours → accès.

Arborescence côté serveur :

```
espace-client/
├── config.php           ← LE CODE D'ACCÈS — créé À LA MAIN sur le serveur, jamais commité
├── protect.php          ← copie de protect.php.example (renommée)
├── index.php            ← <?php require __DIR__.'/protect.php'; header('Location: dashboard/');
├── dashboard/
│   ├── index.php        ← <?php require __DIR__.'/../protect.php'; readfile(__DIR__.'/dashboard.html');
│   ├── dashboard.html   ← le template.html déployé
│   └── data/…
└── presentations/
    └── index.php        ← même garde, puis liste ou readfile du deck
```

`config.php` (créé une fois, directement sur le serveur — via le gestionnaire de fichiers de l'hébergeur ou en SFTP, **jamais via le repo**) :

```php
<?php
return [
  // Choisissez un code long : une phrase de 4-5 mots vaut mieux qu'un PIN.
  'access_code' => 'CHANGEZ-MOI-code-remis-au-client',
  // Sel de signature du cookie : n'importe quelle chaîne aléatoire longue.
  'cookie_salt' => 'CHANGEZ-MOI-chaine-aleatoire-longue',
];
```

Limite connue et assumée : les fichiers statiques (`dashboard.html`, `data/*.json`) restent accessibles à qui connaît leur URL exacte. Pour fermer aussi cet accès direct, ajoutez le `.htaccess` ci-dessous dans `espace-client/`, qui force le passage par les `index.php` gardés :

```apache
# espace-client/.htaccess — bloque l'accès direct aux fichiers statiques,
# seuls les index.php (qui incluent protect.php) restent servis.
<FilesMatch "\.(html|json)$">
  Require all denied
</FilesMatch>
```

…et servez alors les JSON via un petit proxy gardé (`data.php` qui vérifie le cookie puis `readfile()` le JSON demandé, en validant que le nom correspond bien à `^\d{4}-\d{2}$|^index$`). Pour la plupart des clients, l'URL non devinable + le noindex suffisent ; à vous de placer le curseur.

### Option B — `.htaccess` + `.htpasswd` (Basic Auth : plus simple, protège TOUS les fichiers)

Si l'hébergeur est sous Apache et que la fenêtre de login navigateur (grise, non brandée) ne vous dérange pas, Basic Auth protège **tous** les fichiers du dossier, JSON compris, sans PHP :

```apache
# espace-client/.htaccess
AuthType Basic
AuthName "Espace client {{COMPANY_NAME}}"
AuthUserFile /home/{{FTP_USER}}/.htpasswd-espace-client   # chemin ABSOLU, HORS racine web si possible
Require valid-user
```

Génération du `.htpasswd` (en local, puis dépôt sur le serveur — jamais commité) :

```bash
htpasswd -cB /chemin/local/.htpasswd-espace-client client
# saisir le code d'accès au prompt, puis téléverser le fichier en SFTP
```

| | Option A (PHP + cookie) | Option B (Basic Auth) |
|---|---|---|
| Page de saisie aux couleurs de la marque | ✅ | ❌ (popup navigateur) |
| Protège les fichiers statiques (JSON, HTML) | ⚠️ avec le `.htaccess` complémentaire | ✅ nativement |
| Fonctionne sans PHP | ❌ | ✅ (Apache requis) |
| UX client (saisie une fois / 30 j) | ✅ cookie | ⚠️ selon navigateur |

## Règles de gestion du code d'accès

- Le code n'apparaît **nulle part dans le repo** : ni dans un fichier, ni dans un commit, ni dans un exemple. Les fichiers `config.php` / `.htpasswd` sont créés directement sur le serveur.
- Ajoutez le rappel dans `.env` du repo client (`CLIENT_ACCESS_CODE_HINT="voir gestionnaire de mots de passe"`) plutôt que le code lui-même.
- Transmettez le code au client par un canal séparé du lien (le lien par email, le code par SMS/téléphone/gestionnaire partagé).
- Changez le code si la relation client se termine ou en cas de doute de fuite : éditez `config.php` (ou régénérez `.htpasswd`) — effet immédiat, les cookies existants deviennent invalides si vous changez aussi `cookie_salt`.
- `meta name="robots" content="noindex, nofollow"` est déjà dans `template.html` ; ajoutez aussi `Disallow: /espace-client/` dans le `robots.txt` du site.
