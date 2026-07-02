# Registre de vendoring — CRO (marketingskills)

Le template est **standalone au fork** : les capacités CRO sont vendorées (copiées et adaptées) plutôt que dépendantes d'une installation utilisateur. Ce registre trace la provenance, la sélection et la procédure de re-synchronisation.

## Source

| Champ | Valeur |
|---|---|
| Projet | **marketingskills** — Corey Haines (fork utilisé : Littlpinguin) |
| Repo | https://github.com/Littlpinguin/marketingskills (fork de https://github.com/coreyhaines31/marketingskills) |
| Copie locale de référence | `~/.claude/skills/` (skills installées, metadata `version: 1.1.0`) |
| Date de vendoring | **2026-07-02** |
| Licence constatée | **MIT** (fichier `LICENSE` du repo GitHub, vérifié le 2026-07-02 ; description du repo : « Use these however you want ») — permissive, copie/modification/redistribution autorisées avec conservation de la notice |

## Sélection

### Vendoré (adapté en français, condensé, intégré au template)

| Fichier du template | Source dans marketingskills | Rôle |
|---|---|---|
| `.claude/skills/cro-page/SKILL.md` | `page-cro` | Analyse de conversion en 7 dimensions (proposition de valeur, headline, CTA, hiérarchie, preuve, objections, friction) |
| `.claude/skills/cro-form/SKILL.md` | `form-cro` | Optimisation de formulaires : coût par champ, layout, erreurs, bouton, mesure |
| `.claude/skills/cro-popup/SKILL.md` | `popup-cro` | Popups/modales/bannières : déclencheurs, ciblage, fréquence, RGPD, accessibilité |
| `.claude/skills/cro-pricing/SKILL.md` | `pricing-strategy` | Packaging, métrique de valeur, Good-Better-Best, hausse de prix, page tarifs |

Ces skills étaient déjà attendues par la skill `landing-page` du template (table « Skills internes orchestrées ») : le vendoring comble ces références.

### Exclu (et pourquoi)

| Élément source | Raison d'exclusion |
|---|---|
| `lead-magnets` | Déjà couvert — et dépassé — par la skill interne `lead-magnet` (circuit de capture complet, chartage, nurturing) |
| `email-sequence` | Déjà couvert par la skill interne `email` (newsletters, promo, sales, nurturing, intégration outil emailing) |
| `signup-flow-cro`, `onboarding-cro`, `paywall-upgrade-cro`, `churn-prevention` | CRO produit (in-app, post-signup) — hors du périmètre d'une équipe marketing-com ; extension possible pour un client SaaS |
| `ab-test-setup` | Utile mais dépendant d'un outillage d'expérimentation non configuré dans le template ; les skills vendorées formulent les hypothèses A/B, l'exécution reste manuelle ; extension possible |
| `copywriting`, `copy-editing`, `marketing-psychology`, `customer-research`, et le reste du catalogue (~50 skills) | Redondants avec les skills internes du template ou hors périmètre CRO du chantier |
| Dossiers `references/` et `evals/` des skills source | Condensés dans les SKILL.md vendorés ; à re-consulter à la source si besoin de profondeur |

## Adaptations effectuées

- **Traduction française** et condensation (~1 300 lignes source retenues → 4 skills opérationnelles).
- **Étape 0 doctrine `01-brand/`** ajoutée à chaque skill produisant du copy : `checklist-pre-composition.md`, `voice.md`, `messaging-framework.md`, `personas.md` — arrêt et `/start-copilot` si placeholders résiduels. (La source utilisait un `product-marketing-context.md` générique ; remplacé par la doctrine du template.)
- **Règle de preuve du template** : toute preuve sociale/chiffrée recommandée doit exister dans `01-brand/messaging-framework.md` ou être sourcée — jamais de preuve inventée.
- **`brand-check` obligatoire** avant intégration de tout copy produit.
- **Ancrage template** : sorties dans `05-web-content/` et `02-strategy/`, orchestration par `landing-page` et `lead-magnet`, placeholders `{{COMPANY_NAME}}`/`{{COMPANY_MAIN_CONTACT}}`, RGPD par défaut (marché francophone).
- **Garde-fous éthiques renforcés** : interdiction explicite des dark patterns (refus culpabilisant, cases pré-cochées, popups plein écran mobile).

## Procédure de re-sync

1. Consulter le repo source (fork Littlpinguin, et l'upstream coreyhaines31 pour les nouveautés) ; comparer `VERSIONS.md` / les versions `metadata.version` des skills.
2. Vérifier que le `LICENSE` est toujours MIT sur le fork utilisé. Si la licence change ou disparaît, **stopper** et arbitrer (réécriture from scratch en dernier recours).
3. Diff des 4 skills sources (`page-cro`, `form-cro`, `popup-cro`, `pricing-strategy`) contre la version vendorée précédente.
4. Reporter manuellement les changements pertinents (ce sont des **adaptations**, pas des copies : conserver l'étape 0 doctrine, la règle de preuve et les garde-fous — ne jamais écraser).
5. Mettre à jour ce registre (version, date) et le `CHANGELOG.md` du template.
