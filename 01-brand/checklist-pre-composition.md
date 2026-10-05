# Checklist pré-composition — à charger avant TOUTE production

> **Ce fichier est l'étape 0 de toutes les skills de production** (`social-content`, `copywriting`, `email`, `copy-editing`, `seo`, `event-marketing`, `content-strategy`, `slides`, `carousel`, `image-generation`). Aucun texte ne s'écrit, aucun visuel ne se génère, aucun plan ne se brief sans avoir chargé ce fichier **et** `01-brand/voice.md`. Si l'un des deux manque ou contient encore des `{{...}}`, arrêter et lancer `/start-cockpit`.

---

## 1. Règles de voix

- **Position de voix** : {{BRAND_VOICE_POSITION}}
- **Vocabulaire à privilégier** : {{BRAND_VOCABULARY_PREFERRED}}
- **Vocabulaire interdit** : {{BRAND_VOCABULARY_BANNED}}
- **Langue par défaut** : {{BRAND_DEFAULT_LANGUAGE}} — bilinguisme : {{BRAND_BILINGUAL}}
- **Formules signature** : voir la section dédiée de `01-brand/voice.md` — réutiliser les formules validées, ne pas en inventer de nouvelles sans validation.
- **Aucune affirmation sans source** : chaque chiffre publié provient de `01-brand/messaging-framework.md` ou d'une source externe citée. Jamais d'invention, jamais d'arrondi trompeur.

## 2. Règles anti-style-IA

Ces règles neutralisent les tics statistiques de l'écriture générée. Elles s'appliquent à **tout texte destiné à être publié** (post, email, article, titre de slide, légende de carrousel).

### 2a. Vocabulaire IA mort — interdit

Mots sur-représentés dans les sorties de LLM, signature immédiate d'un texte machine. Bannis dans les deux langues :

- **EN** : delve, leverage, seamless, robust, elevate, unlock, harness, empower, streamline, transformative, holistic, synergy, paradigm, game-changer, cutting-edge, groundbreaking, revolutionize, foster, showcase, pivotal, crucial, meticulously, unparalleled, landscape (abstrait), tapestry, realm, journey (abstrait), boast, "serves as" / "stands as" / "marks a" (dire "is").
- **FR** : révolutionner, disruptif, incontournable, booster, levier (abstrait), synergie, paradigme, « plonger dans », « à l'ère de », « dans un monde où », « sans couture », « saisir cette opportunité », « véritable game-changer », « il est important de noter que », « n'hésitez pas à ».

La liste de marque ({{BRAND_VOCABULARY_BANNED}}) s'ajoute à celle-ci, elle ne la remplace pas.

### 2b. Tiret cadratin — interdit

Jamais de tiret cadratin (`—`) dans un contenu visible. Utiliser le demi-cadratin (`–`), une virgule, deux points, des parenthèses, ou reformuler.

### 2c. Parallélismes négatifs et reformulations — faute fatale

Le tic le plus fiable du texte IA : nier un cadrage puis affirmer le « bon ». Un seul suffit à faire échouer le livrable :

- « Ce n'est pas X. C'est Y. » / « Pas X. Y. » / « Oubliez X : Y. »
- « Il ne s'agit pas de X, mais de Y. » / « Moins de X, plus de Y. »
- « X est mort. Y est l'avenir. » / « La question n'est pas X, c'est Y. »
- Versions déguisées : « X semble juste, mais Y est en réalité… », « Bien sûr, X fonctionne. Mais Y… »

**Correction** : supprimer tout ce qui précède l'affirmation positive. Dire ce que c'est, pas ce que ce n'est pas.

### 2d. Structures répétitives à casser

- **Règle de trois automatique** (trois adjectifs, trois segments, à chaque phrase) : préférer 1, 2 ou 4 éléments quand c'est le contenu qui le demande.
- **Rythme métronome** (phrases toutes de même longueur, paragraphes tous de même taille) : varier. Court. Puis plus long. Un fragment parfois.
- **Variation élégante forcée** (synonymes artificiels pour éviter la répétition d'un nom) : répéter le nom, c'est plus clair.
- **Fausse profondeur participiale** (« …, soulignant l'importance de », « …, témoignant de ») : supprimer, ou en faire une phrase avec une affirmation précise.
- **Méta-commentaire** (« Dans cet article, nous allons… », « Voyons ensemble… ») : dire la chose, pas annoncer qu'on va la dire.
- **Emphase gonflée** (« un tournant majeur », « une étape décisive vers ») : énoncer le fait, laisser le lecteur juger l'importance.
- **Fausses amplitudes** (« des traditions ancestrales aux innovations modernes ») : si le milieu de l'intervalle n'existe pas, l'intervalle est faux. Être précis sur une seule chose.
- **Appâts d'engagement** (« Relisez cette phrase. », « Laissez-moi vous expliquer. », « Ça change tout. ») : interdits.
- **Title Case dans les titres** : capitale initiale uniquement (sentence case).

### 2e. Ce qu'on cherche à la place

Paragraphes courts (1-3 phrases). Adresse directe (« vous »). Voix active. Détails concrets : chiffres, noms, dates. Prendre position. S'arrêter quand le point est fait, sans paragraphe de synthèse qui répète ce qui vient d'être lu.

**Garde-fou anti-surapprentissage** : ces règles capturent un goût, pas un algorithme. Les interdits (2a-2c) sont absolus ; le reste s'applique avec jugement. Le test : « est-ce qu'un humain exigeant aurait écrit ça ? »

## 3. Règles typographiques slides et carrousels

- **Jamais de point final sur un titre** : titres, sous-titres, punchlines, CTA courts. Les paragraphes longs (lede, body) gardent leur ponctuation.
- **Tailles minimales lisibles** :
  - Carrousel 1080×1350 : aucun texte sous **22px** source (rendu ~8pt physique sur mobile, la limite).
  - Slides 1920×1080 : aucun texte de contenu sous **18-20px** ; captions ≥ 15px ; seuls les labels mono du chrome (folio, signature) descendent à 12-14px.
- **Échelles déclarées en tokens** : toute taille de police et tout espacement viennent d'une échelle déclarée en tête de fichier. Aucune valeur hardcodée hors échelle.
- **Aucun mot orphelin** en fin de bloc (titre, lede, CTA) ; aucun mot composé coupé en fin de ligne (tiret insécable U+2011 si besoin).
- **Pas d'emoji Unicode décoratif** dans un visuel : utiliser les icônes de marque de `01-brand/assets/` ou en générer via `image-generation`.
- Règles typographiques de marque complémentaires : {{TYPOGRAPHY_RULES}}

## 4. Règle assets — consulter avant de générer

Avant **toute** génération ou création visuelle (image, icône, illustration, portrait, fond) :

1. Lire le catalogue **`01-brand/assets/index.md`** — bibliothèque navigable par rôle et par cas d'usage. On choisit le bon visuel en lisant l'index, sans ouvrir les fichiers.
2. **Un asset existant se réutilise ou se décline, il ne se régénère pas.**
3. Ne jamais se fier au nom brut d'un fichier : se fier à sa fiche dans l'index.
4. Toute nouvelle génération va en staging (`06-graphic-design/outputs/`) ; elle ne devient un asset officiel de `01-brand/assets/` qu'après validation humaine, avec sa fiche ajoutée à `index.md`.

## 5. Règle réutilisation — chercher l'existant avant de créer

Avant de créer un document, un template, un script ou une structure :

1. Consulter **`_templates/inventory.md`** — l'inventaire de ce qui existe déjà dans le repo (templates, scripts, composants, gabarits).
2. Scanner les productions passées du dossier concerné (`examples/`, `editions/`, `outputs/`, `decks/`).
3. Créer du neuf est le **dernier recours**, jamais le réflexe. Si on crée, on référence la nouveauté dans l'inventaire.

---

## Sanction

Si un point de cette checklist échoue à la relecture → **retour en rédaction, pas de livraison**. Le `brand-check` final (5 points : vocabulaire / ton / preuve / audience / visuel) reste obligatoire en sortie ; cette checklist est son miroir en entrée.
