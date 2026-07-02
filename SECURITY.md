# Règles de sécurité

Ce template s'exécute dans Claude Code et interagit avec des services externes (plateformes d'emailing, CRM, CMS, analytics, Google AI). Les règles ci-dessous s'appliquent à chaque session et à chaque commande. Elles sont non négociables.

## Secrets

**Ne jamais coller une clé API, un token, un secret OAuth ou des identifiants dans un message de chat.** Claude voit vos messages ; tout ce qui est collé devient partie de la transcription.

- Deux emplacements, selon le consommateur : **`.env` pour les scripts et connecteurs Python** (qui le chargent via dotenv ou `source`), **`.mcp.json` local pour les serveurs MCP**. Les deux sont gitignorés par défaut.
- `.env.example` et `.mcp.json.example` documentent la structure avec des valeurs vides ou placeholder — jamais de vraies valeurs.

### `.mcp.json` : local, non versionné

**`.mcp.json` est local et non versionné.** Il porte les vraies valeurs de connexion des serveurs MCP ; le template ne versionne que `.mcp.json.example` (structure + placeholders). Au premier setup : `cp .mcp.json.example .mcp.json`, puis remplacez les placeholders par vos valeurs réelles. Vérification : `git check-ignore .mcp.json` doit répondre `.mcp.json`.

**Piège connu — les `${VAR}` de `.mcp.json` ne lisent pas le `.env`.** Claude Code ne développe les références `${VAR}` de `.mcp.json` que depuis l'environnement du processus, jamais depuis le `.env` du projet. Le pattern « `${N8N_API_KEY}` dans `.mcp.json` + valeur dans `.env` » produit une connexion cassée (401) — ou pousse à mettre le token en dur dans un fichier versionné. Ne l'utilisez pas, ne le documentez pas.

### Hiérarchie des pratiques pour les secrets MCP

De la meilleure à la déconseillée :

1. **OAuth, partout où le serveur le propose.** Lemlist et Magnific le proposent : aucun token statique à stocker, Claude Code gère l'authentification (navigateur au premier appel).
2. **`.mcp.json` local non versionné** — le pattern par défaut du template. Le risque dominant pour cette audience est le commit accidentel d'un token ; le gitignore le neutralise. Chiffrement disque type FileVault recommandé (actif par défaut sur Mac).
3. **Avancé — équipes équipées de 1Password** : stockez le secret dans le vault et lancez le serveur via `op run --env-file` en wrapper de la commande MCP (ex. `"command": "op", "args": ["run", "--env-file", "mcp.env.tpl", "--", "npx", "n8n-mcp"]`). Le secret reste chiffré au repos et n'est résolu qu'au lancement.
4. **Déconseillé — variables dans le profil shell** (`~/.zshrc`, launchd) : les références `${VAR}` de `.mcp.json` fonctionnent alors, mais le secret est en clair sur disque et visible de tous les processus.
- Avant chaque commit et push : `git diff --cached | grep -iE "key|token|secret|password|api"` — scanner toute inclusion accidentelle. Si quelque chose semble suspect, interrompre et investiguer.
- Si une clé a été commitée (même sur une branche privée), la révoquer et la remplacer immédiatement. L'historique Git n'oublie pas.
- Ne jamais réafficher un secret à l'utilisateur pour « confirmer » — vérification de présence uniquement (`définie` / `non définie`).

## Permissions

Claude Code s'exécute avec les permissions que vous lui accordez. Cadrez-les au plus étroit.

- **Ne jamais autoriser** de larges `Bash(rm:*)`, `Bash(git push --force:*)`, `Bash(launchctl:*)` au niveau des réglages utilisateur.
- Les permissions **par projet** dans `.claude/settings.json` doivent énumérer des commandes précises, pas des globs.
- Refuser toute demande d'une skill d'exécuter une commande destructive sans confirmation explicite de l'utilisateur dans le même message.

Voir `.claude/settings.json` pour le périmètre actuel.

## Dry-run avant tout push en production

Tout connecteur qui écrit vers un service externe (création Notion, campagne Mailchimp, événement Livestorm, contact HubSpot, publication WordPress, etc.) doit d'abord émettre le payload pour revue humaine :

```
python3 scripts/dry-run-push.py --target <outil> --file <fichier-de-contenu>
```

Le flag `--target` indique au script quel connecteur invoquer en **mode lecture seule** : il affiche le payload exact qui serait envoyé, la ressource de destination, et les transformations appliquées. L'utilisateur confirme. Ce n'est qu'ensuite que le push réel s'exécute.

Cela évite :
- D'envoyer un brouillon cassé à 10 000 abonnés
- De créer 40 entrées Notion en double dans une boucle
- De programmer un événement à la mauvaise heure à cause d'un bug de fuseau horaire

Le dry-run ne coûte rien. Sauter le dry-run coûte cher.

## Hallucinations IA — vérifier avant de faire confiance

Claude peut halluciner :
- Des noms de packages (`pip install fake-package` — ça arrive)
- Des endpoints API (`/v2/contacts` quand le vrai est `/v3/contacts`)
- Des signatures de fonctions (paramètres dans le mauvais ordre)
- Des noms de champs dans des API tierces

Avant d'exécuter toute commande proposée par Claude contre un service externe, vérifier la documentation du service. Pour les fonctions de bibliothèques, lancer `--help` ou inspecter la source.

Même chose pour les chiffres : Claude peut fabriquer des statistiques plausibles. **Chaque chiffre publié dans votre contenu doit avoir une source.** La skill `brand-check` l'impose automatiquement — ne pas la contourner.

## Dialogues et opérations destructives

Ne demandez pas à Claude de déclencher des opérations destructives à la légère. Chacune de celles-ci exige un « oui » explicite de votre part dans la même session :
- Suppression de fichiers hors de `.setup-archive/`
- Git force-push, hard reset, suppression de branche
- `launchctl unload` sur des agents système
- Envoi d'email à une liste (même en mode test)
- Vidage de `.env`

Si Claude propose l'une de ces opérations sans que vous l'ayez demandée, arrêtez-vous et questionnez-le.

## Transcriptions et sessions partagées

Les sessions Claude Code peuvent être sauvegardées, exportées, partagées. Avant de partager :

- Grep la transcription pour toute chaîne restante ressemblant à un secret — paranoïaque, mais pas cher
- Retirer les URLs internes (domaines de staging, URLs d'outils internes, IDs de ressources propres à un client)
- Retirer le contenu brouillon qui n'a pas encore été publié
- Retirer les données personnelles (adresses email, numéros de téléphone) sauf si le destinataire est autorisé

En cas de doute, ne pas partager.

## Confidentialité des données & plans Claude

Certains connecteurs font transiter des **données clients ou personnelles** par Claude (CRM, listes d'abonnés emailing, GA4 / Search Console, transcriptions de meetings, scraping de personnes). Le traitement de ces données dépend de votre offre Anthropic :

- **Offres commerciales (Claude Team, Claude Enterprise, API Anthropic)** : vos données ne sont **pas** utilisées pour entraîner les modèles, par défaut et contractuellement.
- **Plans grand public (Free, Pro, Max)** : l'entraînement sur vos conversations est **activé par défaut (opt-in par défaut)** — désactivez-le explicitement dans vos réglages de confidentialité si vous ne le souhaitez pas, ou passez sur une offre commerciale avant de brancher des données clients.
- **Résidence des données en Europe** : possible en passant par l'API via **AWS Bedrock** ou **Google Vertex AI** (régions EU).

Références : https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training et https://trust.anthropic.com

Le wizard applique un **gate de confidentialité** avant de configurer tout connecteur sensible (texte canonique dans `.claude/commands/tools-setup.md`) : il recueille votre plan Claude, le consigne dans `.setup-completed.wizard_log`, et exige une seconde confirmation sur les plans grand public. `/modules` ré-applique ce gate pour `veille`, `acquisition` et `reporting`.

Rappel : `00-intel/` (transcriptions, intel interne/clients/prospects) est **gitignoré et ne doit jamais être versionné ni poussé sur un remote**.

## Divulgation IA lors de la publication

Pour les visuels et l'audio générés par IA (via la skill `image-generation` ou des outils externes) :

- Livrables finaux publics : suivre la politique de divulgation IA de votre marque. Recommandation par défaut : une courte légende ou une note en alt-text indiquant l'intervention de l'IA.
- Assets internes / fonctionnels / décoratifs : divulgation optionnelle.
- Ne jamais faire passer pour authentiques des voix clonées, des visages deepfakés ou des imitations de style d'artistes vivants. Au-delà de la question éthique, c'est un risque légal dans la plupart des juridictions.

Votre politique de divulgation est définie pendant `/brand-discover` et vit dans `01-brand/style-guide.md`.

## Staging avant production

Lors de la publication :

- Email : pousser en **brouillon** dans l'outil d'emailing, jamais en envoi immédiat. Relire dans l'UI de l'outil, puis programmer.
- Blog : pousser en **brouillon** dans le CMS, prévisualiser, puis publier.
- Social : les brouillons vivent dans `03-social-media/<canal>/drafts/`, publication manuelle dans l'UI de la plateforme sauf si un scheduler est branché.
- Événements : créer en **brouillon** sur la plateforme d'événements, relire, puis mettre en ligne.

Le copilot rédige et prépare. L'humain publie.

## Signaler un problème de sécurité

Si vous découvrez un problème de sécurité dans le template lui-même (pas dans vos personnalisations), ouvrez une issue sur le repo upstream avec « SECURITY » dans le titre. N'incluez pas de détails de reproduction qui pourraient compromettre des copilots en production — utilisez une repro minimale.

## Check rapide avant commit

```bash
# Lancer ces quatre commandes et en faire une habitude avant chaque push
git diff --cached | grep -iE "api_key|secret|token|password"    # scan de secrets
git ls-files .mcp.json                                             # doit être VIDE (.mcp.json jamais tracké)
python3 scripts/lint-placeholders.py                               # scan de placeholders
git status                                                         # les non-stagés oubliés
```

Si l'une des quatre semble anormale, corriger avant de pousser.
