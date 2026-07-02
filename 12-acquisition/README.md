# 12-acquisition — prospection B2B multicanale pilotée par le copilot

> **Module optionnel.** L'acquisition sortante (outbound) via une **plateforme d'outreach externe**, pilotée depuis Claude Code. Le copilot apporte l'intelligence (ciblage, voix de marque, listes, analyse) ; la plateforme apporte l'exécution (séquences, multicanal, délivrabilité, opt-out). Avant toute campagne : lire `conformite-rgpd.md`.

## Le principe : chacun son métier

| | Qui s'en charge |
|---|---|
| ICP et personas de campagne, nourris par la doctrine et le terrain | **Le copilot** (`01-brand/` + `00-intel/`) |
| Rédaction des séquences dans la voix de la marque | **Le copilot** (checklist doctrine + brand-check obligatoires) |
| Constitution et qualification des listes | **Le copilot** (skill scraping/Apify ou export de votre outil de sourcing) |
| Analyse des résultats de campagne | **Le copilot** (via MCP, versé dans `11-reporting/`) |
| Séquences et relances, multicanal email + LinkedIn | **La plateforme** |
| Délivrabilité, warm-up, plages et volumes d'envoi | **La plateforme** |
| Opt-out / désinscription technique | **La plateforme** |
| Tracking (ouvertures, clics, réponses, intérêt) | **La plateforme** |

Ce découpage évite le piège classique des deux côtés : les templates génériques « voix de robot » des plateformes, et la reconstruction artisanale d'une infrastructure d'envoi (délivrabilité, opt-out) que des outils spécialisés gèrent mieux.

## Plateforme primaire : Lemlist (serveur MCP officiel)

[Lemlist](https://www.lemlist.com) expose un **serveur MCP officiel** ([doc de setup](https://developer.lemlist.com/mcp/setup), OAuth ou clé API) : Claude crée les campagnes et les séquences, gère les leads et lit les statistiques **directement depuis la conversation**. C'est ce qui en fait le choix par défaut de ce module — aucune couche d'intégration à construire.

Guide complet : **`setup-lemlist.md`** (connexion MCP pas à pas + workflow type d'une campagne de bout en bout).

<!-- Mainteneur du template : vous pouvez placer ici votre lien de parrainage/referral Lemlist. -->
Créer un compte Lemlist : {{LEMLIST_SIGNUP_URL}}

## Alternative documentée : Salesforge

Pas de serveur MCP officiel à ce jour, mais une API REST + webhooks qui se pilotent depuis des scripts ou depuis n8n si le module `10-automatisations/` est actif. Le workflow copilot (brief → ICP → liste → séquence → suivi) reste identique ; seule l'exécution change d'outil. Voir la section dédiée dans `setup-lemlist.md`. La même logique s'applique à toute plateforme d'outreach sérieuse disposant d'une API.

## Ce que le copilot fait concrètement

1. **ICP / personas de campagne** — dérivés de `01-brand/personas.md` (qui achète, pourquoi, avec quelles objections) et affûtés par `00-intel/` : besoins réellement exprimés en rendez-vous, secteurs qui répondent, objections récurrentes. Pas de persona de brainstorming hors-sol.
2. **Séquences dans la voix de la marque** — un cold email est un contenu de marque comme un autre : il respecte `01-brand/voice.md` (ton, vocabulaire banni), les règles anti-style-IA de la doctrine, et passe le **brand-check** avant push. Une preuve concrète par message, jamais de claim sans source.
3. **Listes qualifiées** — via la skill de scraping/Apify du copilot sur des sources publiques ciblées, ou l'export de votre outil de sourcing ; puis double relecture de pertinence (copilot + humain par échantillon) avant import. Une liste courte et juste bat une liste large.
4. **Lecture des résultats** — points de campagne réguliers via le MCP (envois, ouvertures, réponses, intérêt), agrégés dans `11-reporting/` ; les réponses qualitatives (objections, questions) sont recopiées dans `00-intel/inbox/` pour nourrir les prochains ciblages et les contenus des autres modules.

## Contenu du module

| Fichier | Rôle |
|---|---|
| `setup-lemlist.md` | Connexion du MCP Lemlist + workflow type d'une campagne de bout en bout (+ alternative Salesforge) |
| `conformite-rgpd.md` | Cadre légal de la prospection B2B en France/UE — **lecture obligatoire avant la première campagne** |
| `campagnes/` | Une fiche par campagne : persona, justification du ciblage, séquence, résultats (créé à la première campagne) |

## Règles du module

- **Relecture humaine avant chaque campagne** : ciblage, séquence, mention d'information. Le copilot ne lance jamais un envoi seul.
- **Brand-check obligatoire** sur chaque séquence, comme pour tout contenu du copilot.
- **RGPD** : pertinence du ciblage et mention d'information sont votre responsabilité même si la plateforme gère l'opt-out — voir `conformite-rgpd.md`.
- **Aucun secret dans ce dossier** : clé API dans `.env` (référencée par `.mcp.json`), jamais en clair dans un fichier committé.
