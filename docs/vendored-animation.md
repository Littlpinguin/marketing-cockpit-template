# Registre des skills animation vendorisées

Ce template fonctionne en **standalone au fork** : les meilleures skills animation externes ont été copiées et adaptées dans `.claude/skills/` plutôt que référencées comme dépendances de plugins. Ce fichier est le registre de traçabilité : source, licence, adaptations, procédure de re-synchronisation.

Date de vendorisation : **2026-07-03**.

## Vue d'ensemble

| Skill du template | Source | Version source | Licence | Statut |
|---|---|---|---|---|
| `.claude/skills/animation-gsap/` | [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) (freshtechbro), plugin `gsap-scrolltrigger`, skill `gsap-scrolltrigger` | v1.0.0 | MIT | ✅ Vendorisée |
| `.claude/skills/animation-animejs/` | idem, plugin `animation-components`, skill `animejs` | v1.0.0 | MIT | ✅ Vendorisée |
| `.claude/skills/animation-lottie/` | idem, plugin `animation-components`, skill `lottie-animations` | v1.0.0 | MIT | ✅ Vendorisée |
| `.claude/skills/animation-scroll-reveal/` | idem, plugin `animation-components`, skill `scroll-reveal-libraries` | v1.0.0 | MIT | ✅ Vendorisée |
| — | plugin `animation-components`, skills `react-spring-physics` et `animated-component-libraries` | v1.0.0 | MIT | ⛔ Non vendorisées (React-only, hors périmètre : les livrables web du template sont des fichiers HTML/CSS/JS autonomes) |
| — | plugins `threejs-webgl` et `meta-skills` (`web3d-integration-patterns`) | v1.0.0 | MIT | ⛔ Non vendorisées (3D/WebGL : trop lourd et rarement justifié pour une page marketing ; réévaluable au besoin) |

Licence constatée sur disque au moment de la copie : fichier `LICENSE` à la racine du dépôt claudedesignskills — MIT, © 2025 Claude Skills Project.

## Périmètre retenu

Pour chaque skill : **`SKILL.md` + `references/*.md` uniquement.**

Ce qui n'a **pas** été copié, et pourquoi :

- `scripts/*.py` (générateurs de boilerplate, timeline builders) : politique du template — aucun script externe n'est copié ni exécuté sans audit (cf. `vendored-design.md`, même règle). Les SKILL.md mentionnent encore ces scripts dans leur section « Resources » ; cette mention est inopérante et documentée ici.
- `assets/` (starters HTML, visualiseurs d'easing, exemples) : redondants avec les templates du dossier `05-web-content/` et le catalogue de slides ; réduisent le bruit au fork.

Adaptations effectuées :

- `name:` du frontmatter renommé (`animation-gsap`, `animation-animejs`, `animation-lottie`, `animation-scroll-reveal`) pour suivre la convention de nommage par famille du template.
- Footer d'attribution ajouté en fin de chaque `SKILL.md`.
- `description:` réécrite en 300 caractères au plus et mise entre guillemets (audit d'architecture, 2026-11-04), pour tenir dans le budget de la liste des skills.
- Corps des `SKILL.md` ramené sous 500 lignes (même audit) : les sections Common Patterns, Integration Patterns et, pour GSAP, Advanced Techniques sont déplacées telles quelles dans `references/common_patterns.md` (GSAP : `references/scrolltrigger_recipes.md`) et `references/integration_patterns.md`. Leur titre reste dans le `SKILL.md`, suivi d'un renvoi ; une section « Fichiers de référence » suit l'aperçu ; une table des matières est ajoutée en tête des références amont qui n'en avaient pas.

## Cas d'usage dans le template

Ces skills servent aux livrables web (`05-web-content/`) : landing pages, lead magnets, pages d'offre. Retour d'expérience fondateur (jessem.fr, 2026-07-03) : reprise du système de reveal maison par GSAP + ScrollTrigger (compteurs de stats, staggers, parallaxe scrub, timeline de charnière narrative). Deux garde-fous à réutiliser systématiquement :

1. **`prefers-reduced-motion`** : désactiver toutes les animations JS et laisser un fallback CSS.
2. **Reveals bidirectionnels** : un élément masqué en `opacity: 0` doit se révéler quel que soit le sens du scroll ET si la page se charge déjà scrollée (restauration de position navigateur). Pattern : `gsap.set` initial + `ScrollTrigger.create` avec `onEnter` + `onEnterBack` + déclenchement immédiat si `st.progress > 0`. Ne jamais utiliser `gsap.from` + `once: true` seul : les éléments au-dessus du viewport restent invisibles au reload mi-page.
3. **CSP** : GSAP auto-hébergé (`assets/js/vendor/`) plutôt qu'un CDN si le site sert `script-src 'self'`.

## Procédure de re-synchronisation

1. `claude plugin marketplace add freshtechbro/claudedesignskills` puis `claude plugin install <plugin>@claude-design-skillstack`.
2. Comparer `~/.claude/plugins/cache/claude-design-skillstack/<plugin>/<version>/skills/<skill>/` avec la copie locale (`diff -ru`, en ignorant `name:` et `description:` du frontmatter, le footer, la section « Fichiers de référence », les renvois et les tables des matières ajoutées). Une section déplacée se compare au fichier de `references/` qui la contient.
3. Reporter les changements utiles, conserver renommage + footer, mettre à jour la version dans ce registre.
