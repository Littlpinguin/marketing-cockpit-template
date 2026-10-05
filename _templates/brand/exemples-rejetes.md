---
title: "Corpus de rejets de {{COMPANY_NAME}}"
type: brand-reference
version: 1.0
updated: {{SETUP_DATE}}
tags: [marque, redaction, corpus-negatif, brand-check]
---

# Corpus de rejets

## À quoi sert ce fichier

Les exemples publiés apprennent à un agent ce que la marque fait. Ce fichier lui apprend ce que la marque a refusé, et pourquoi. Les deux se lisent ensemble : les skills de rédaction (`social-content`, `email`, `copywriting`) chargent ce corpus au même moment que les archives du canal, avant de rédiger une ligne.

Un rejet enregistré ici n'est pas une faute de goût : chaque entrée renvoie à une règle écrite, à sa section exacte, et porte la version corrigée qui a été retenue. Une entrée sans règle citée n'a rien à faire dans ce fichier.

## Comment lire les entrées

**Les extraits fautifs sont dans des blocs de code.** C'est volontaire : `scripts/lint-brand.py` ignore les lignes prises dans une clôture de trois accents graves, donc les tirets longs, les hashtags et les parallélismes négatifs de ces extraits ne déclenchent aucun constat. Le reste du fichier, corrections comprises, est scanné normalement.

Ce que le linter contrôle réellement sur ce fichier : les **tirets longs** et les **points finaux de titres** (en erreur), ainsi que les **parallélismes négatifs** (en avertissement). Deux règles ne le couvrent pas et se relisent donc à l'œil : `hashtags`, bornée aux chemins de `03-social-media`, et `forbidden-words`, qui ne descend qu'au rang d'avertissement sous `01-brand/` puisque la doctrine cite les mots qu'elle interdit. Une erreur du linter ici signale qu'une **correction retenue** est elle-même fautive, et se corrige sur-le-champ.

**Les extraits sont reconstitués.** Ils illustrent un motif de rejet ; aucun n'est la copie d'un contenu réellement publié, et aucun n'est attribué à un auteur. Les prénoms qui y apparaissent sont fictifs : vérifier qu'aucun ne correspond à une vraie personne de l'entreprise avant d'ajouter une entrée. Les vraies personnes se citent depuis leurs sources validées, jamais depuis ce fichier.

## Format d'une entrée

Une entrée se compose toujours de cinq champs, dans cet ordre :

1. **Titre** : `### AAAA-MM-JJ · canal · motif en trois mots`
2. **Extrait fautif** dans un bloc de code, cinq lignes au maximum, marqué « exemple reconstitué »
3. **Motif** : ce qui cloche, en une ou deux phrases, sans jugement de valeur
4. **Règle** : fichier et section exacte, vérifiée comme existante au moment de l'écriture
5. **Correction retenue** : la version publiée, hors bloc de code, donc conforme au linter

## Comment ajouter une entrée

C'est l'étape 5 de la skill `brand-check` qui alimente ce fichier : tout verdict 🔴 BLOCK qui porte sur la forme, la voix ou la construction s'y inscrit. Les blocages purement factuels (chiffre qui contredit `messaging-framework.md`, date fausse, lien mort) restent hors corpus : ils se corrigent, ils n'enseignent rien sur la voix.

Le brand-check qui ajoute une entrée le dit dans son rapport, avec le titre de l'entrée créée. Écrire l'extrait fautif tel qu'il a été produit, sans l'adoucir, et sans le rattacher à un auteur : ce qui compte est le patron, jamais la personne. Contrôle après ajout : `python3 scripts/lint-brand.py 01-brand/exemples-rejetes.md`.

---

## Entrées

Les quatre premières entrées sont des exemples d'amorçage fournis par le gabarit du cockpit. Elles illustrent des règles valables pour toute marque ; les remplacer au fil des vrais rejets.

### {{SETUP_DATE}} · LinkedIn · parallélisme négatif

Exemple reconstitué :

```
Ce n'est pas un outil de plus. C'est une nouvelle façon de travailler.
Notre équipe accompagne les directions marketing depuis trois ans.
Envie d'en savoir plus ? Écrivez-nous.
```

**Motif** : la première phrase nie une formulation pour en affirmer une autre à sa place, sans rien ajouter de factuel. C'est le signe le plus reconnaissable d'un texte produit par une machine, et il suffit à lui seul à bloquer une livraison.

**Règle** : `01-brand/anti-ai-writing-style.md` § « 3F. Le plus grave (fatal) : parallélismes négatifs ».

**Correction retenue** : « Inès a remplacé ses trois tableurs de suivi par un seul écran, un mardi matin, en quarante minutes. »

---

### {{SETUP_DATE}} · Email · tirets longs

Exemple reconstitué :

```
Notre atelier revient — deux jours à Lyon — et le programme est enfin
en ligne. Au menu : des cas concrets et un long dîner.
Les places sont limitées — réservez avant le 30.
```

**Motif** : trois tirets cadratins en trois lignes. Ils installent une respiration molle là où la marque veut des phrases nettes, et ils signent le texte de machine avant même qu'on en lise le fond.

**Règle** : `01-brand/anti-ai-writing-style.md` § « 2. Règles de mise en forme ».

**Correction retenue** : « Notre atelier revient : deux jours à Lyon, et le programme est enfin en ligne. Les places sont limitées, réservez avant le 30. »

---

### {{SETUP_DATE}} · Landing page · point final sur un titre

Exemple reconstitué :

```
# Pilotez vos campagnes sans changer d'outil.

Deux jours d'ateliers pour reprendre la main.
Inscriptions ouvertes jusqu'au 30.
```

**Motif** : le titre se termine par un point. Il ferme la lecture à l'endroit précis où il devait la lancer, et la même faute se propage ensuite aux objets d'email et aux textes de visuels tirés de la page.

**Règle** : `01-brand/voice.md` § « Typography rules », règle « No final period on a title ».

**Correction retenue** : point retiré du titre, le corps gardant sa ponctuation normale : « Pilotez vos campagnes sans changer d'outil »

---

### {{SETUP_DATE}} · Newsletter · chiffre non sourcé

Exemple reconstitué :

```
Neuf entreprises sur dix prévoient d'augmenter leur budget marketing
cette année, et la plupart ne mesurent toujours pas leur retour.
Le marché n'a jamais été aussi encombré.
```

**Motif** : le chiffre ne vient d'aucune source, il est formulé comme un fait établi, et la phrase suivante enchaîne une seconde affirmation sans preuve.

**Règle** : `01-brand/messaging-framework.md`, chiffres clés (aucun chiffre publié hors doctrine sans référence externe citée) ; contrôle de l'étape 2.6 de la skill `brand-check`.

**Correction retenue** : chiffre retiré faute de source ; la phrase garde le seul fait vérifiable, attribué à son étude (titre, date, taille d'échantillon), ou disparaît.

---

## Ce que ce fichier n'est pas

- ❌ Un journal des corrections mineures : une coquille, une virgule ou un lien mort ne s'y consignent pas
- ❌ Un registre nominatif : aucun extrait n'est attribué à un auteur, un contenu réel ou une personne
- ❌ Une liste de mots interdits : elle vit dans `scripts/lint-brand.toml`, alimentée par `voice.md` et `anti-ai-writing-style.md`
- ❌ Un substitut aux exemples publiés : il se lit **en plus** des archives du canal (`03-social-media/*/examples/`, `04-email/newsletter/editions/`), jamais à leur place
