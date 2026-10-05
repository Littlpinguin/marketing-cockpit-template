---
title: "Doctrine anti-style-IA de {{COMPANY_NAME}}"
type: brand-reference
updated: {{SETUP_DATE}}
tags: [redaction, anti-ia, liste-noire, brand-check]
---

# Doctrine anti-style-IA

Ce fichier dit comment écrire pour que rien ne sonne produit par une machine. Il se lit **avant** toute rédaction (règle préventive) et se repasse en relecture. La voix propre de la marque vit dans `voice.md` : quand les deux divergent sur un choix de ton (tutoiement, contractions, première personne), `voice.md` l'emporte ; sur la liste noire, ce fichier l'emporte.

Les sections 3A, 3B, 3D, 3E et 3F sont reprises telles quelles par `scripts/lint-brand.toml` (règles `forbidden-words` et `negative-parallelism`) : un mot ajouté ici s'ajoute aussi là-bas, sinon le linter et la doctrine divergent. La skill `humanize-writing` est la passe **curative** qui applique ce fichier à un texte déjà écrit.

---

## 1. Règles d'écriture

Écrire comme une personne précise qui se trouve taper au clavier.

**Rythme**
- Paragraphes courts : une ou deux phrases par défaut, trois au maximum.
- Entrer dans le sujet tout de suite, sans tour de chauffe.
- Varier la longueur des phrases. L'IA écrit comme un métronome (toutes les phrases de longueur moyenne, tous les paragraphes de trois ou quatre phrases) : casser ce rythme.
- Chaque nouveau paragraphe introduit idéalement une opposition (« mais ») ou une conséquence (« donc ») par rapport au précédent : c'est ce qui fait avancer un récit. Une succession d'ajouts (« et puis ») le fait piétiner.
- Le point est fait ? S'arrêter. Ne pas résumer ce que le lecteur vient de lire.

**Voix et ton** (dans les limites de `voice.md`)
- S'adresser au lecteur, voix active. L'IA se réfugie dans le passif et la troisième personne.
- Être précis : des chiffres, des noms, des détails concrets. L'écriture précise est une écriture nette.
- Dire son incertitude simplement quand elle existe (« probablement », « je crois »). L'IA n'hésite jamais ; un humain, si.
- Ne jamais rembourrer pour paraître exhaustif. Court et juste vaut mieux que long et flou.
- Prendre position. L'IA écrit comme quelqu'un qui a peur de s'engager (« pourrait », « est souvent considéré comme ») : s'engager.
- Donner de vrais exemples, tirés de ce qui s'est réellement passé, plutôt qu'un « imaginons un scénario où ».
- Préférer des verbes physiques pour des processus abstraits (« poncé », « boulonné », « dépouillé »).
- L'humour vient de la précision : être inattendument exact.
- Les apartés entre parenthèses sont bienvenus (commentaire éditorial, réaction franche, autodérision).
- Transitions naturelles uniquement, jamais de connecteur mécanique.

---

## 2. Règles de mise en forme

- Paragraphes courts (une ou deux phrases par défaut, trois au maximum).
- Nombres en chiffres (3 ans, 10 outils, 500 utilisateurs).
- **Aucun tiret cadratin (U+2014).** L'IA en abuse. Utiliser virgule, point, deux-points, point-virgule ou parenthèses. Si la marque bannit aussi le demi-cadratin (U+2013), le dire dans `voice.md` et l'ajouter à `[dashes]` de `scripts/lint-brand.toml`.
- Gras avec parcimonie : un ou deux moments clés par section.
- Blocs de code pour les commandes, prompts ou sorties d'outils précis.
- La mise en forme s'utilise comme le sel : titres, puces et listes numérotées seulement quand ils servent.
- Pas de paragraphe de synthèse qui reformule tout ce qui précède.

---

## 3. Liste noire

Une seule occurrence suffit à faire échouer un texte.

### 3A. Vocabulaire mort

Ces mots sont statistiquement surreprésentés dans les textes produits par des modèles de langage. Ils en sont l'empreinte. Ne jamais les employer.

**Anglais** : delve, realm, harness, unlock, tapestry, paradigm, cutting-edge, revolutionize, landscape (abstract), intricate/intricacies, showcasing, crucial, pivotal, surpass, meticulously, vibrant, unparalleled, underscore (verb), leverage, synergy, innovative, game-changer, testament, commendable, meticulous, highlight (verb), emphasize, boast, groundbreaking, align, foster, showcase, enhance, holistic, garner, accentuate, pioneering, trailblazing, unleash, versatile, transformative, redefine, seamless, optimize, scalable, robust, breakthrough, empower, streamline, frictionless, elevate, adaptive, effortless, data-driven, insightful, proactive, mission-critical, visionary, disruptive, reimagine, unprecedented, intuitive, leading-edge, synergize, democratize, accelerate, state-of-the-art, dynamic, immersive, predictive, transparent, proprietary, integrated, plug-and-play, turnkey, future-proof, paradigm-shifting, supercharge, enduring, interplay, valuable, captivate

Également bannis en anglais quand ils servent à éviter « is » ou « has » : « serves as », « stands as », « marks a », « represents a », « boasts a », « features a », « offers a ». Dire simplement « is ».

**Français** : disruptif, révolutionner, révolutionnaire, incontournable, booster, « plonger dans », « à l'ère de », « dans un monde où ». La liste longue des tics français vit dans la skill `humanize-writing` (passes 2 et 3).

### 3B. Tournures mortes

- « In today's [anything]… » / « À l'ère de… », « Dans un monde où… »
- « It's important to note that… » / « It's worth noting… » / « Il est important de noter que… », « Force est de constater… »
- « In order to » (dire « to ») / « Afin de » (dire « pour »)
- « I'd be happy to help »
- « Straightforward »
- « Let's dive in » / « Let's explore » / « Let's unpack » / « Delve into » / « Plongeons dans… »
- « At the end of the day » / « Au final »
- « Moving forward »
- « To put this in perspective… »
- « What makes this particularly interesting is… »
- « The implications here are… »
- « In other words… »
- « It goes without saying… » / « Il va sans dire… »
- « Here's the part nobody's talking about » / « What nobody tells you » / « Ce que personne ne vous dit »
- Toute phrase avec « nobody » ou « most people don't realize » / « la plupart des gens ignorent »
- « In this article, I will… » / « Dans cet article, nous allons… » (tout métacommentaire sur ce qu'on va dire)
- « Despite its [positive words], [subject] faces challenges… »
- « Challenges and Future Prospects » / « Défis et perspectives » comme titre de section

### 3C. Transitions mortes

- « Furthermore » / « Additionally » / « Moreover » / « De plus » / « Par ailleurs » / « En outre »
- « That said » / « That being said » / « Cela dit »
- « With that in mind » / « Dans cette optique »
- « It is also worth mentioning » / « Il convient également de mentionner »
- « On top of that »
- Tout connecteur mécanique qui sent la dissertation

Cette section n'est pas reprise par le linter (trop fréquente en prose correcte) : elle se juge à la relecture.

### 3D. Appâts d'engagement

- « Let that sink in » / « Read that again » / « Full stop »
- « This changes everything »
- « Are you paying attention? » / « You're not ready for this »
- « N'hésitez pas à… » en fin de post

### 3E. Langage hype

- « Supercharge » / « Unlock » / « Future-proof »
- « 10x your [anything] »
- « Game-changer » / « Cutting-edge »
- Toute promesse de superpouvoir, de richesse facile ou de transformation du jour au lendemain

### 3F. Le plus grave (fatal) : parallélismes négatifs

**Les constructions qui nient une formulation pour en affirmer une autre.** C'est le signe le plus fiable d'un texte produit par une machine. L'IA en dépend parce qu'elles donnent à une idée mince l'air d'être profonde. Si une seule apparaît, réécrire toute la phrase.

**Patrons bannis**
- « This isn't X. This is Y. » / « Ce n'est pas X. C'est Y. »
- « Not X. Y. » / « Pas X. Y. »
- « Forget X. This is Y. » / « Oubliez X. Voici Y. »
- « Less X, more Y. » / « Moins de X, plus de Y. »
- « Not only X, but also Y. » / « Non seulement X, mais aussi Y. »
- « It's not just about X, it's about Y. » / « Il ne s'agit pas seulement de X, il s'agit de Y. »
- « No X, no Y, just Z. » / « Pas de X, pas de Y, juste Z. »
- « X? No. Y. » / « X ? Non. Y. »
- « Stop thinking X. Start thinking Y. » / « Arrêtez de penser X. Pensez Y. »
- « It's not about X. It's about Y. »
- « X is dead. Y is the future. » / « X est mort. Y est l'avenir. »
- « The question isn't X. The question is Y. » / « La question n'est pas X. »
- « You don't need X. You need Y. » / « Vous n'avez pas besoin de X. Vous avez besoin de Y. »
- « X is overrated. Y is what matters. »
- « Ce n'est pas X, c'est Y » et « non pas X mais Y »
- TOUTE phrase qui rejette un cadrage, puis le remplace par un cadrage corrigé.

**Les versions déguisées**
- « Si X peut sembler juste, Y est en réalité… » (même patron sous un imperméable)
- « Bien sûr, X fonctionne. Mais Y est là où… » (concession puis pivot : même squelette)
- « X attire toute l'attention, mais Y est ce qui compte vraiment… »

**Pourquoi c'est si important** : chaque modèle en génère des dizaines par réponse, parce que le patron abonde dans l'écriture persuasive (conférences, copy marketing, tribunes). Quand le lecteur le voit, son cerveau enregistre : machine.

**La correction est simple** : supprimer tout ce qui précède l'affirmation positive. « Ce n'est pas une question d'outil, c'est une question de méthode » devient « C'est une question de méthode. » Le cadrage nié n'apporte aucune information.

Ne pas confondre avec l'enchaînement narratif par « mais » (section 1) : le « mais » narratif relie deux faits qui s'opposent ; le parallélisme négatif nie une formulation pour en affirmer une autre.

---

## 4. Patterns d'écriture IA à éviter

### 4A. Inflation d'importance

« Un moment charnière dans l'évolution de… », « Marquant un tournant vers… », « Posant les jalons de… ». Énoncer le fait, laisser le lecteur juger de sa portée.

### 4B. Règle de trois

L'IA adore lister trois choses (« rapidité, efficacité et innovation ») pour donner à une analyse mince l'air d'être complète. Dire deux choses, ou quatre, ou la seule qui compte.

### 4C. Fausses amplitudes

« Des traditions ancestrales aux innovations modernes. » Si l'on ne sait pas nommer ce qu'il y a de significatif entre les deux bornes, l'amplitude est fausse : la supprimer et être précis sur une chose.

### 4D. Variation élégante forcée

La pénalité de répétition pousse l'IA à alterner les synonymes : une personne devient « le protagoniste », puis « l'acteur clé », puis « la figure centrale ». Répéter le nom : un synonyme forcé est pire qu'une répétition.

### 4E. Métacommentaire

« Dans cette section, nous allons voir… », « Voici un tour d'horizon complet de… ». Dire la chose, sans annoncer qu'on va la dire.

### 4F. Fausse profondeur participiale

L'IA accroche des participes présents pour simuler l'analyse : « soulignant son importance », « reflétant des tendances plus larges ». Supprimer la proposition ; si l'analyse compte, elle mérite sa propre phrase avec une affirmation précise.

### 4G. Clauses de date de connaissance

« À ma connaissance… », « Bien que les détails soient limités… ». Ne jamais les inclure : sourcer ou supprimer.

### 4H. Fuites de conversation

« J'espère que cela vous aide ! », « Excellente question ! », « Bien sûr ! ». Elles appartiennent au chat, jamais à un texte publié.

### 4I. Rythme métronome

Toutes les phrases de même longueur, tous les paragraphes du même nombre de phrases. Un texte réel respire de façon inégale : court, puis plus long, puis un fragment, puis une phrase de trente mots qui mérite sa longueur.

### 4J. Évitement de la copule

L'IA remplace « est » et « a » par « constitue », « se positionne comme », « représente », « incarne ». Dire « est ». Les verbes simples fonctionnent.

### 4K. Majuscules de titre

L'IA met une majuscule à chaque mot d'un titre (« Contexte Mondial : La Demande En Hausse »). Écrire les titres en casse de phrase.

---

## 5. Guide anti-surapprentissage

Ce document décrit un goût. C'est un guide : l'appliquer avec jugement.

**Niveaux de règle**
- **RÈGLE DURE** : ne jamais enfreindre. Mots, tournures et structures de la liste noire. Absolu.
- **FORTE TENDANCE (70 à 80 %)** : phrases courtes, adresse directe, voix active, détails précis, rythme varié.
- **LÉGÈRE PRÉFÉRENCE (le contexte décide)** : choix de mots particuliers, structures, place de l'humour. Sans étiquette, considérer qu'il s'agit d'une légère préférence.

**La variation naturelle compte**
- Ne pas réutiliser la même formule d'ouverture à chaque fois parce qu'elle a marché.
- Un mot de la liste noire peut, très rarement, être le seul mot juste : le justifier dans le rapport de brand-check.
- Laisser le contenu dicter la structure.

**Le test final**

> Est-ce que cela ressemble à quelque chose que la marque écrirait vraiment, ou à une IA qui s'efforce de l'imiter ?

Si cela sonne forcé, revenir en arrière et habiter la voix.
