---
name: cro-popup
description: Créer ou optimiser un popup, une modale, un slide-in ou une bannière de conversion pour {{COMPANY_NAME}} — capture email, lead magnet, exit intent, annonce. Convertir sans agacer ni abîmer la marque : déclencheurs, ciblage, fréquence, copy, accessibilité, conformité RGPD/Google. Utiliser quand l'utilisateur dit « popup », « exit intent », « modale », « bannière d'annonce », « capturer des emails avec un popup » ou « sticky bar ». Orchestrée par la skill landing-page (uniquement sur demande explicite).
---

# cro-popup — popups et modales de conversion

Adapté du plugin marketingskills (Corey Haines / fork Littlpinguin, MIT) — voir `docs/vendored-cro.md`.

## Étape 0 — Doctrine de marque (OBLIGATOIRE)

Un popup est du copy à haute visibilité et à haut risque d'agacement :

1. `01-brand/checklist-pre-composition.md` et `01-brand/voice.md` — voix, vocabulaire, interdits. Les formules manipulatrices type « Non, je ne veux pas économiser » sont un interdit absolu quel que soit le vocabulaire de la marque.
2. `01-brand/style-guide.md` — le popup est charté (couleurs, typo, radius) comme n'importe quel livrable.
3. `01-brand/personas.md` — l'offre du popup doit parler au persona de la page.

Si un fichier manque ou contient des `{{...}}` : arrêter et lancer `/start-copilot`.

## Principes

1. **Le timing fait tout** : trop tôt = interruption ; trop tard = occasion manquée ; au bon moment = offre utile.
2. **La valeur doit être évidente** : bénéfice immédiat, pertinent pour la page, qui vaut l'interruption.
3. **Respecter l'utilisateur** : fermeture facile, pas de piège, mémoriser le refus, ne jamais dégrader l'expérience.

## Déclencheurs

| Déclencheur | Usage | Notes |
|---|---|---|
| **Clic** (l'utilisateur initie) | lead magnets, contenus gated, démo | Zéro agacement — à privilégier par défaut |
| **Scroll** (25-50%) | articles, contenus longs | Signal d'engagement réel |
| **Temporel** | visiteurs génériques | Jamais < 30 s ; 30-60 s minimum |
| **Exit intent** | dernière chance | Desktop seulement ; offre différente du popup d'entrée |
| **Comportemental** | pages tarifs, visites répétées | Segments à forte intention |

## Types

- **Capture email** : bénéfice spécifique (pas « Abonnez-vous »), un seul champ, fréquence annoncée (« Un email par mois, 5 min de lecture »)
- **Lead magnet** : montrer ce qu'on obtient (aperçu/couverture), promesse tangible, livraison immédiate — circuit complet via skill `lead-magnet`
- **Exit intent** : reconnaître le départ, traiter une objection, offre finale distincte
- **Bannière d'annonce** : haut de page, un seul message, dismissible, limitée dans le temps (événements → skill `event-marketing`)
- **Slide-in** : coin/bas d'écran, ne bloque pas le contenu — l'option la moins intrusive

## Design

- Hiérarchie : headline → bénéfice → formulaire/CTA → option de refus
- Desktop : 400-600 px, jamais plein écran ; mobile : slide-up bas d'écran, **jamais d'overlay plein écran** (pénalité interstitiels intrusifs de Google + expérience dégradée)
- **Croix visible en haut à droite**, cliquable/tapable (l'utilisateur qui ne trouve pas la fermeture quitte le site) ; clic hors popup et touche Échap ferment aussi
- Refus en texte : « Non merci » / « Plus tard » — poli, jamais culpabilisant

## Copy (dans la voix de la marque — étape 0)

- Headline : bénéfice (« Obtenez [résultat] »), question, ou preuve sociale réelle (chiffre sourcé doctrine)
- Sous-titre : précise la promesse, lève l'objection (« Zéro spam »), cadre la fréquence
- CTA : première personne et spécifique — « Recevoir mon guide » plutôt que « Valider »

## Fréquence et ciblage

- Max 1 affichage par session ; mémoriser le refus (cookie/localStorage) 7-30 jours
- Exclure : visiteurs déjà convertis, refus récents, pages de checkout/conversion
- Cibler : nouveaux vs récurrents, source de trafic (cohérence avec le message de l'annonce), type de page

## Conformité et accessibilité

- **RGPD** : consentement clair, lien politique de confidentialité, jamais de case pré-cochée
- **Accessibilité** : navigable clavier (Tab/Entrée/Échap), focus trap pendant l'ouverture, contraste suffisant, compatible lecteur d'écran
- **Google** : les interstitiels intrusifs pénalisent le SEO mobile — bannières raisonnables OK

## Mesure et repères

Suivre : taux d'affichage, conversion (affichages → soumissions), taux de fermeture immédiate. Repères indicatifs : popup email 2-5% ; exit intent 3-10% ; déclenché au clic 10%+ (auto-sélection).

## Format de sortie

Spécification complète par popup : type, déclencheur, ciblage, fréquence, copy (headline / sous-titre / CTA / refus), notes design (desktop + mobile), règles de non-conflit si plusieurs popups. Livrer dans `05-web-content/`. Copy validé par `brand-check` avant intégration.

## Skills associées

- `lead-magnet` — l'offre derrière le popup et son circuit de nurturing
- `cro-form` — le formulaire dans le popup
- `cro-page` — la page qui accueille le popup
- `email` — ce qui se passe après la capture
