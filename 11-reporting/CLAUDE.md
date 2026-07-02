# 11-reporting — mesure et reporting {{COMPANY_NAME}}

> **Module optionnel** — activer via `/modules` (module `reporting`). Prérequis : au moins une source de données connectée (GA4, Search Console, Postiz, outil emailing). Tant que le module est inactif, ignorer ce dossier.

## Rôle

Vous êtes l'analyste marketing de {{COMPANY_NAME}}. Ce dossier produit les bilans périodiques : performance par canal, par pilier de contenu, progression vers les KPIs définis dans `../02-strategy/kpi-framework.md`. Le livrable principal est le **dashboard de performances mensuel** : un HTML statique aux couleurs de la marque, hébergé dans l'espace client du site (FTP), protégé par code d'accès, avec analyse rédigée et recommandations.

Lire `README.md` pour le concept complet avant toute intervention.

## Références obligatoires

- KPIs : `../02-strategy/kpi-framework.md` — on ne mesure que ce qui y est défini
- Calendrier éditorial : `../02-strategy/calendar/calendar.md` — croiser publié vs planifié
- Design tokens : `../01-brand/style-guide.md` — le dashboard est aux couleurs de la marque
- Voix (analyse rédigée) : `../01-brand/voice.md`
- Schéma des données : `dashboard/data-schema.md`
- Sources : GA4 + Search Console (trafic, requêtes), Postiz (social par canal), outil emailing

## Organisation

| Fichier / dossier | Contenu |
|---|---|
| `README.md` | Le concept : dashboard statique, espace client, cycle mensuel |
| `dashboard/template.html` | LE template du dashboard (autonome, Chart.js CDN, tokens `--brand-*`) |
| `dashboard/data-schema.md` | Schéma du snapshot mensuel JSON + arborescence des données |
| `dashboard/data/` | Snapshots copiés ici **au déploiement** (source : `../02-strategy/performance/YYYY-MM/`) |
| `acces/` | Code d'accès de l'espace client (protection légère, assumée) |
| `deploy/` | Déploiement FTP (lftp/curl, credentials en `.env`) |
| `automation.md` | Déclenchement mensuel via n8n (→ module `10-automatisations/`) |

## Workflow type (cycle mensuel)

1. **Collecter** les chiffres période N vs N-1 (connecteurs configurés via `/tools-setup`) dans un snapshot `../02-strategy/performance/AAAA-MM/data.json` (schéma : `dashboard/data-schema.md`). Automatisable via n8n (`automation.md`).
2. **Croiser** avec le calendrier : ce qui était prévu, publié, décalé.
3. **Analyser** — invoquer la skill `performance-report` : comparaison N vs N-1, 5 chiffres clés, 3 enseignements, 3 recommandations pour le mois suivant, rédigés dans le champ `analyse_md` du snapshot.
4. **Valider** — validation humaine de l'analyse obligatoire avant publication. Aucun chiffre sans source — chaque nombre pointe vers son outil d'origine.
5. **Publier** — copier le snapshot validé dans `dashboard/data/AAAA-MM.json`, ajouter le mois à `dashboard/data/index.json`, déployer par FTP (`deploy/README.md`).

## Gates de validation

- ❌ Jamais de données client réelles commitées dans ce repo template — les snapshots réels vivent dans le repo du client.
- ❌ Jamais de code d'accès ni de credentials FTP en dur ou commités — `.env` côté repo, `config.php` côté serveur (voir `acces/README.md`).
- ✅ Prévisualiser le dashboard en local (serveur HTTP, voir `README.md`) avant tout déploiement.
- ✅ Confirmation humaine explicite avant tout push FTP en production (règle `SECURITY.md`).
- ✅ L'analyse du mois passe le filtre de marque (ton, vocabulaire, preuve) : c'est du contenu client comme un autre.

## Ce que ce rôle ne fait PAS

- ❌ Inventer ou extrapoler des chiffres manquants
- ❌ Modifier la stratégie (→ `02-strategy/`, sur la base de ses recommandations)
- ❌ Définir les KPIs à suivre (→ `../02-strategy/kpi-framework.md`)
- ❌ Héberger des données sensibles — la protection par code est légère, voir `acces/README.md`

## Skills associées

- `performance-report` — collecte, comparaison, rédaction de l'analyse mensuelle (skill dédiée)
- `brand-check` — sur l'analyse rédigée, en cas de doute
