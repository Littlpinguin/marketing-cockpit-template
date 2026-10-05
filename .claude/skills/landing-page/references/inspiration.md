# Recherche d'inspiration

Deux recherches partent en parallèle dès la phase 0 (agent `landing-researcher`), puis chaque agent de section lit leur synthèse. Une référence se regarde en images : elle ne se juge jamais sur son titre ni sur sa description.

## 1. Benchmark de pages qui convertissent

- **Sources** : recherche web et lecture de pages publiques.
- **Volume** : 8 à 12 pages du même type d'offre (formation, atelier, logiciel en essai, prestation, événement, liste d'attente…), de préférence chez des acteurs reconnus du secteur et chez des concurrents directs (`02-strategy/veille/` s'il existe).
- **Pour chaque page** : ordre des sections, nature de la preuve, rendu du programme ou de l'offre, rareté, choix de formule, CTA (libellé, nombre, destination), traitement mobile.
- **Synthèse** : 10 motifs récurrents, 5 idées distinctives, erreurs à éviter, bonnes pratiques UX. Sources citées, aucun chiffre fabriqué, 1 200 mots au plus.

## 2. Inspiration visuelle

### Galeries publiques

| Source | Ce qu'on y cherche |
|---|---|
| Dribbble | Compositions de section, objets signatures, traitements de cartes et de billets |
| Awwwards, Godly, One Page Love | Pages complètes de haut niveau : rythme, mise en scène au défilement, typographie |
| Land-book, Lapa Ninja, Landingfolio, SaaS Landing Page | Landings par type d'offre : ordre des sections, blocs de prix, formulaires |
| Codrops | Techniques d'animation et de défilement expliquées pas à pas |
| 21st.dev, Aceternity UI, Magic UI, Animata, React Bits, Free Frontend | Composants : défilement collant, révélation, billet, arborescence, frise, FAQ |
| Vitrine GSAP et démos CodePen de l'éditeur | Épinglage, scrub, tracés SVG, textes découpés |

**Méthode qui marche** :

1. Certaines galeries répondent vide ou refusent un accès automatisé (réponse 202 sans contenu, ou 403). Utiliser alors le navigateur intégré, **uniquement sur des sites tiers publics**, jamais sur un environnement local, de préproduction ou un compte connecté.
2. Sur une galerie à recherche (Dribbble, par exemple) : ouvrir la page de recherche, relever les vignettes (lien, titre, image), composer une planche-contact en grille et la capturer, puis ouvrir en grand les maquettes retenues.
3. Si une navigation est refusée, ne pas la contourner : le dire et passer à la source suivante.
4. Aucune donnée personnelle collectée.

**Requêtes qui donnent de bons résultats** : `course landing page`, `workshop landing page`, `bootcamp landing page`, `saas pricing section`, `pain points section`, `choose your path`, `learning path`, `course curriculum`, `scrollytelling`, `sticky scroll`, `ticket design`, `boarding pass`, `testimonial wall`, `two column faq`, `kinetic typography`, `line art landing page`.

### Points de départ par besoin

Des composants publics qui ont déjà servi de base. Une nouvelle landing cherche les siens.

| Besoin | Points de départ |
|---|---|
| Parcours en défilement collant | Aceternity UI « Sticky Scroll Reveal » |
| Billet ou carte d'offre | 21st.dev (composants « ticket »), Free Frontend « CSS Tickets » |
| Révélation au défilement | Codrops, articles sur les effets de révélation |
| Choix entre deux formules | Animata « Tilted Card » |
| Carte ou schéma tracé au défilement | Codrops, animations de cartes SVG pilotées par le défilement ; Aceternity UI « World Map » |
| Arborescence de fichiers | 21st.dev et Magic UI, composants « File Tree » |
| FAQ avec carte collante | 21st.dev, FAQ en deux colonnes |
| Scènes épinglées | Démos GSAP de panneaux épinglés ; reproduction en `position: sticky` plutôt qu'en épinglage par script |

Pour chaque besoin retenu : 2 ou 3 références vérifiées, la technique CSS et JS pour la reproduire dans un HTML statique (vanilla, ou GSAP si la page le justifie), et le comportement en mouvement réduit.

## 3. Filtre de marque, à mettre dans chaque prompt de recherche

- **À garder** : ce que dit `01-brand/style-guide.md` (palette de `01-brand/tokens.json`, polices de la marque, rayons, style d'illustration).
- **À écarter, en disant pourquoi** : les tropes bannis de `01-brand/style-guide.md`, les marqueurs du look IA de `01-brand/design-anti-generique.md` § 1 (dégradé violet par défaut, emojis en icônes, héros centré par réflexe, excès d'animation, cartes de faible densité, les trois clusters récents), les ressorts et rebonds, la photo de banque d'images générique, et toute signature déjà portée par une autre page de la marque.

## 4. Consolidation

Tout atterrit dans `05-web-content/landing-pages/<slug>/pilotage/research-notes.md` :
- la synthèse du benchmark ;
- les références retenues, rangées par besoin de section (hero, problème, choix, parcours, offre…) ;
- pour chacune, ce qu'on en prend ;
- une liste « Écartés », motivée.

Le rapport de chaque agent de section cite les 3 références qui lui ont le plus servi.
