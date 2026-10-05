# Doctrine design anti-générique — à charger avant TOUTE production visuelle

> **Ce fichier est le pendant visuel de la section 2 de `checklist-pre-composition.md`** (qui couvre le texte). Il fait partie de l'étape 0 des skills de production visuelle (`slides`, `carousel`, `image-generation`, `landing-page`, `design-system`, `design-direction`, `design-taste`, `brandkit`) et s'applique à tout HTML livré, dashboard `11-reporting` compris. Chaque règle est sourcée : les URLs sont en fin de fichier, numérotées [1]-[7].

**Principe racine.** Le look générique ne vient pas du médium, il vient de l'acceptation des défauts. L'homogénéisation visuelle du web est mesurable dès 2007, bien avant l'IA générative : entre 2010 et 2019 la distance de layout entre sites a chuté de 44 % (la distance couleur de 32 %), et cette similarité est corrélée à 0,77 (p < 0,001) avec l'usage partagé des mêmes librairies front-end — pendant que le code source natif, lui, devenait *moins* similaire [6]. Conséquence pratique : chaque valeur par défaut non questionnée (framework, palette, police, layout) est un pas vers le template. La règle de fond n'est pas « éviter tel style », c'est **ne jamais livrer un choix qu'on n'a pas fait**.

---

## 1. Marqueurs du look IA — interdits par défaut

Ces marqueurs sont documentés par Anthropic même (« defaults rather than choices... they appear regardless of subject ») [1][2] et codifiés indépendamment par plusieurs systèmes de design [3][4][5]. « Interdits par défaut » signifie : on ne les livre jamais par réflexe ; on peut les utiliser si la marque l'exige (§5) ou si un choix argumenté le justifie par écrit.

### 1a. Gradient violet sur fond blanc

Le cliché n°1, nommé verbatim dans le cookbook Anthropic (« clichéd color schemes, particularly purple gradients on white backgrounds ») [1]. Codifié deux fois de plus : ui-ux-pro-max le liste comme anti-pattern pour les industries de confiance (banque, fintech, santé, juridique, assurance, secteur public) [3] ; le skill Taste impose un « Lila Ban » strict (« no purple button glows, no neon gradients ») avec pour alternative une base neutre Zinc/Slate + un seul accent à fort contraste [4].

- **Règle** : jamais de violet ni de gradient violet-rose par défaut. Base neutre + un accent tranché.
- **Nuance contextuelle (du rapport)** : ui-ux-pro-max recommande le violet... pour les produits IA/chatbot [3]. Le ban est contextuel, pas universel — et si la marque est violette, la marque prime (§5).

### 1b. Polices par défaut : Inter, Roboto, Arial, Open Sans, Lato, system fonts

Listées comme « overused font families » par Anthropic, avec l'interdit explicite « Never use: Inter, Roboto, Open Sans, Lato » [1]. Note d'évolution : la v1.1.0 (juin 2026) du skill frontend-design a remplacé les bans nominaux par une exigence plus profonde — un choix typographique délibéré et non-défaut [2].

- **Règle** : une police est choisie pour une raison qu'on peut énoncer, jamais parce qu'elle était là. Si le style-guide de la marque impose une de ces familles, on la garde (§5) et on compense par le layout, la densité et l'élément signature.

### 1c. Emojis comme icônes

Marqueur codifié dans deux systèmes : checklist ui-ux-pro-max « No emojis as icons (use SVG: Heroicons/Lucide) », règle `no-emoji-icons` [3] ; skill Taste : emojis bannis du code, du markup et des alt, icônes Phosphor/Radix en priorité [4].

- **Règle** : tout pictogramme structurel (feature, liste, KPI, navigation) est un SVG d'un vrai set — **Heroicons, Lucide ou Phosphor** — jamais un emoji.

### 1d. Héros centrés systématiques

Le skill Taste les bannit par défaut au profit de layouts asymétriques : split-screen 50/50, contenu à gauche / asset à droite, white-space asymétrique, grilles masonry ou fractionnaires, fallback single-column sous 768 px [4].

- **Règle** : l'asymétrie est le défaut ; un héro centré reste permis quand c'est un choix argumenté, pas un réflexe.
- **Confiance moindre (du rapport)** : position d'un seul skill, vérifiée mais votée 2-1 — à appliquer avec jugement, pas comme un absolu.

### 1e. Excès d'animation

« Extra animation contributes to the feeling that the design is AI-generated » (frontend-design, Anthropic) [2].

- **Règle** : **un seul moment de motion orchestré** par page (le reveal d'entrée, ou un élément signature animé), pas des effets dispersés sur chaque bloc. Cohérent avec la doctrine slides du template : transitions d'entrée uniquement, mascottes et motifs fixes.

### 1f. Frankenstein layouts et faible densité d'information

Documentés empiriquement par NN/g (déc. 2025, testé sur Lovable, Bolt, Figma Make, Claude, Replit) : éléments superflus, informations répétées, flux illogique, « visually prominent containers with low information density » — la hiérarchie visuelle contredit la priorité du contenu [5]. (Limite notée par le rapport : l'étude porte sur un seul type de tâche.)

- **Règle** : chaque conteneur gagne sa proéminence par son contenu. Pas de carte qui n'existe que pour remplir une grille, pas d'information répétée pour meubler.

### 1g. Les trois clusters récents (à éviter « quel que soit le sujet »)

Ajoutés par Anthropic dans frontend-design v1.1.0 (juin 2026) comme les trois looks où le design généré se concentre actuellement [2] :

1. fond crème (~`#F4F1EA`) + serif à fort contraste + accent terracotta ;
2. fond quasi-noir + accent unique vert acide ou vermillon ;
3. layout façon broadsheet : filets hairline, border-radius 0.

- **Règle** : si le brief mène naturellement vers l'un de ces trois looks, le tordre (autre accent, autre grille, élément signature fort) pour qu'il redevienne un choix et non un défaut statistique.

---

## 2. Pratiques pro — ce qu'on fait à la place

### 2a. Direction artistique intentionnelle

La question n'est pas « comment » utiliser Grid, Flexbox ou Shapes, mais « quand » et « pourquoi » (Clarke, *Art Direction for the Web*) [7]. Avant la première ligne de code, chaque livrable a un point de vue esthétique défendable en une phrase.

### 2b. Contrastes typographiques extrêmes

Règles chiffrées d'Anthropic : graisses en extrêmes — 100/200 contre 800/900, jamais 400 contre 600 ; sauts de taille de 3x et plus, pas de 1,5x [1]. Et 2+ rôles typographiques : un display de caractère utilisé avec retenue, un body discret complémentaire, un utility pour data et captions [2]. La typographie est le levier de différenciation n°1 : chaque famille porte « tone, texture, and timbre » [7] — l'expressivité se joue sur le display, le body reste sobre.

Familles distinctives par registre, proposées par le cookbook Anthropic [1] — suggestions à filtrer par la marque (§5), jamais des impositions :

- code / data : JetBrains Mono, Fira Code ;
- éditorial : Playfair Display, Fraunces ;
- startup / display : Clash Display, Satoshi ;
- technique : IBM Plex ;
- distinctif : Bricolage Grotesque.

### 2c. Grilles éditoriales

La grille a une fonction narrative au-delà de l'alignement : cohésion compositionnelle, guidage du regard, ordre de lecture — en contraste explicite avec les designs homogènes produits par les frameworks standard [7]. Le layout est un instrument de hiérarchie : il dicte où va l'attention.

### 2d. Densité d'information

L'inverse du Frankenstein layout : montrer plus avec moins de chrome. Un tableau dense et lisible bat trois cartes creuses ; un chiffre en display énorme adossé à sa source bat un badge décoratif [5].

### 2e. Couleur : dominantes + accents tranchés

S'engager sur une esthétique cohérente via variables CSS. « Dominant colors with sharp accents outperform timid, evenly-distributed palettes » [1] — une palette timide également distribuée est un tell de non-décision.

### 2f. Élément signature

Chaque page a UN élément dont on se souvient : « the single unique element this page will be remembered by » [2]. Si la marque possède déjà une signature (gradient, motif, mascotte, style d'illustration), l'amplifier avant d'inventer — c'est le premier candidat (cf. skill `design-direction`).

---

## 3. Workflow imposé — deux passes avant le code

Adapté du skill frontend-design v1.1.0 d'Anthropic [2] et des tests NN/g [5] :

1. **Plan de tokens compact**, avant tout code : palette en 4-6 valeurs hex nommées ; typographies pour 2+ rôles ; concepts de layout en descriptions d'une phrase + wireframes ASCII ; l'élément signature nommé explicitement.
2. **Auto-critique contre le brief** : relire ce plan et réviser toute partie qui « se lit comme le défaut générique » [2] — palette qui pourrait servir n'importe quel client, police prise par habitude, héro centré par réflexe, cluster §1g. Seulement ensuite, écrire le code.
3. **Données et contenus réalistes, jamais placeholder** : fournir le vrai contenu (ou un mock JSON réaliste) guide vers un design centré sur le contenu réel [5]. Vrais chiffres sourcés via `01-brand/messaging-framework.md`, vrais noms, vraies longueurs de texte. « John Doe », « Acme » et le lorem ipsum sont interdits.
4. **Spécificité de prompt** (quand on délègue à un modèle image ou design) : guider chaque dimension séparément — typographie, couleur, motion, fonds [1] ; nommer des styles reconnus plutôt que des adjectifs vagues (« neobrutalist » bat « moderne ») — la spécificité prime sur la verbosité [5].

---

## 4. Checklist de pré-livraison mesurable

Issue de ui-ux-pro-max v2.10.0 [3] — binaire, vérifiable, non négociable pour tout HTML livré :

- [ ] Contraste texte ≥ **4.5:1** en mode clair (et en mode sombre le cas échéant).
- [ ] **Focus states** visibles au clavier sur tout élément interactif.
- [ ] `cursor: pointer` sur tout élément cliquable.
- [ ] Transitions **150-300 ms** ; `prefers-reduced-motion` respecté.
- [ ] Responsive vérifié à **375 / 768 / 1024 / 1440 px**.
- [ ] Zéro emoji structurel — icônes SVG uniquement (§1c).
- [ ] Zéro placeholder (§3.3) — chaque chiffre a une source, chaque nom est réel.

---

## 5. Hiérarchie : la marque prime

**`01-brand/style-guide.md` et `01-brand/voice.md` PRIMENT sur cette doctrine.** Si la marque est violette, elle reste violette ; si sa police est Inter, on garde Inter — et on compense par le layout, la densité et l'élément signature. Cette doctrine gouverne **l'espace laissé libre par la marque** : là où le style-guide est muet, les interdits §1 et les pratiques §2 s'appliquent pleinement ; là où il parle, il fait foi.

Ordre de préséance en cas de conflit : **marque (style-guide) > cette doctrine > préférences génériques des skills**.

**Garde-fou anti-surapprentissage** — même logique que la section 2 de `checklist-pre-composition.md` : ces règles capturent un goût, pas un algorithme. Les marqueurs §1 sont des interdits *par défaut*, pas des lois : un design qui les évite tous peut rester générique, un design qui en assume un peut être excellent — si c'est un choix. Le test : « est-ce qu'un directeur artistique exigeant pourrait défendre chaque choix de cette page ? »

---

## Sources

Rapport de deep-research vérifié adversarialement (juillet 2026, 12 findings). Références :

- [1] Anthropic — *Prompting for frontend aesthetics* (cookbook, oct. 2025) : <https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics>
- [2] Anthropic — skill `frontend-design` v1.1.0 (juin 2026, plugin officiel Claude Code) : <https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md>
- [3] nextlevelbuilder — skill `ui-ux-pro-max` v2.10.0 (juin 2026) : <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>
- [4] BND-1 — *Taste skill* (« Lila Ban », `no-emoji-icons`, héros asymétriques) : <https://github.com/BND-1/taste-skill> ; miroir : <https://github.com/sickn33/antigravity-awesome-skills/blob/main/skills/design-taste-frontend/SKILL.md> ; variante : <https://github.com/Leonxlnx/taste-skill>
- [5] Nielsen Norman Group — *Prompt to Design Interfaces* / vague prototyping (Wang, déc. 2025) : <https://www.nngroup.com/articles/vague-prototyping/>
- [6] Goree, Doosti, Crandall & Su — *Investigating the Homogenization of Web Design*, CHI 2021 (peer-reviewed) : <https://dl.acm.org/doi/abs/10.1145/3411764.3445156>
- [7] Andy Clarke — *Art Direction for the Web* (2019) : <https://web.archive.org/web/20190602111018/https://stuffandnonsense.co.uk/artdirectionfortheweb/> ; corroboré par <https://www.smashingmagazine.com/2019/07/inspired-design-decisions-pressing-matters/>
