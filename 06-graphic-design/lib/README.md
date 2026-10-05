# 06-graphic-design/lib — base de composition et police locale

Ce dossier porte ce que partagent toutes les compositions HTML capturées en image (visuels sociaux, infographies, cartes) : `compose.css`. Les carrousels de `scripts/build-carousel.py` s'appuient sur la même police locale.

## `compose.css`

À linker dans tout HTML de composition, en chemin relatif (ici depuis `06-graphic-design/outputs/`) :

```html
<link rel="stylesheet" href="../lib/compose.css">
```

Il importe deux fichiers, sans jamais écrire une valeur de marque lui-même :

| Import | Rôle | Qui le remplit |
|---|---|---|
| `01-brand/assets/fonts/fonts.css` | `@font-face` de la police de marque, servie en local | vous, une fois (voir ci-dessous) |
| `06-graphic-design/presentations/tokens.css` | couleurs, dégradé, familles, motif de marque | `/brand-discover` |

Il ajoute quelques aides préfixées `compo-` (texte en dégradé, motif en filigrane, halo d'ambiance, chiffre clé). La mise en page reste sur mesure pour chaque visuel.

Capture : `06-graphic-design/scripts/compose-screenshot.sh <compo.html> <sortie.png> [largeur] [hauteur]`. Contrôle avant et après capture : `06-graphic-design/scripts/qa-visuel.py`.

## Installer la police de marque en local

Chrome headless ne patiente pas pour une webfont distante : sans fichier local, la capture sort en police de repli (souvent Helvetica), et le PDF d'un carrousel aussi. La police se sert donc depuis le dépôt.

1. **Vérifier la licence avant toute copie.** Une police n'est pas un asset comme un autre : il faut le droit de l'**embarquer** (web et PDF), pas seulement de l'installer sur un poste. Les polices sous **SIL Open Font License** (la plupart des Google Fonts) l'autorisent. Une police commerciale exige le plus souvent une licence « webfont » ou « embedding » distincte de la licence desktop : la lire, et en cas de doute ne pas copier le fichier. Noter la licence et sa source au registre des droits de la marque.
2. **Déposer les fichiers** `.woff2` dans `01-brand/assets/fonts/` (un fichier variable suffit le plus souvent ; séparer `latin` et `latin-ext` par `unicode-range` si la fonderie les livre ainsi).
3. **Écrire `01-brand/assets/fonts/fonts.css`**, qui déclare chaque fichier. Le nom de famille doit être **exactement** celui de `font.*` dans `01-brand/tokens.json` et de `--font-display` dans `tokens.css` : c'est lui que les QA comparent.

   ```css
   @font-face{
     font-family:'Ma Police';font-style:normal;font-weight:100 900;
     font-display:block;            /* Chrome attend la police avant de capturer */
     src:url('ma-police-variable.woff2') format('woff2');
   }
   ```

   Les `url()` y sont relatives à `fonts.css` lui-même.
4. **Vérifier** : ouvrir une composition, zoomer sur un mot en bas de casse et le comparer à la police attendue. `qa-visuel.py` contrôle la famille déclarée, pas le fichier effectivement chargé : seul l'œil, ou un PDF inspecté (`pdffonts`), confirme que la police locale a bien servi.

Le dossier `01-brand/assets/` est propre à chaque projet : le template public n'embarque aucune police, et une police sous licence commerciale ne se versionne que dans un dépôt privé dont la licence couvre l'usage.
