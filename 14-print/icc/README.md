# Profils ICC des papiers

Ce dossier reçoit les profils ICC utilisés par `../lib/build.sh` pour séparer en CMJN et déclarer l'intention de sortie PDF/X-4. **Les fichiers `.icc` ne sont jamais versionnés** (règle dans `.gitignore`) : les profils de l'ECI (European Color Initiative) peuvent être utilisés et embarqués dans un PDF sans restriction, mais pas redistribués. On les télécharge donc une fois par machine.

## Lequel télécharger

| Papier ou support | Profil | Nom de fichier attendu | Paquet sur le site de l'ECI |
|---|---|---|---|
| Non couché (offset, recyclé, naturel), cas le plus courant | PSO Uncoated v3 (FOGRA52) | `PSOuncoated_v3_FOGRA52.icc` (défaut de `build.sh`) | `pso-uncoated_v3_fogra52.zip` |
| Couché (brillant, mat, satiné), imprimeur récent | PSO Coated v3 (FOGRA51) | `PSOcoated_v3.icc` | `pso-coated_v3.zip` |
| Couché, imprimeur qui exige encore FOGRA39 ; film ou toile de grand format | ISO Coated v2 (FOGRA39) | `ISOcoated_v2_eci.icc` | `eci_offset_2009.zip` |

Téléchargement : page « Downloads » du site de l'ECI, https://www.eci.org/en/downloads (rubrique des profils offset). Dézipper et copier le fichier `.icc` ici, sous le nom exact du tableau.

**Le profil se choisit avec l'imprimeur**, pas de mémoire : certains imprimeurs en ligne demandent FOGRA52 sur non couché, d'autres ISO Coated v2 sur tous les papiers. La fiche technique du produit configuré fait foi ; on la consigne dans le README de la production.

## Comment la chaîne le trouve

- `build.sh` cherche `$ICCDIR/$ICC_FICHIER`, avec `ICCDIR=14-print/icc` et `ICC_FICHIER=PSOuncoated_v3_FOGRA52.icc` par défaut. Un profil ailleurs sur la machine : `export ICCDIR=/chemin/du/dossier`.
- Autre papier : `export ICC_FICHIER=PSOcoated_v3.icc` (ou `ISOcoated_v2_eci.icc`) ; `build.sh` en déduit la condition de sortie (FOGRA51, FOGRA39) déclarée dans le PDF. Penser à aligner `OUTPUT_ID` et `TAC_MAX` pour `verify.py` (330 % sur FOGRA39, 300 % sur FOGRA51 et FOGRA52).
- `blacktext.py` reçoit le profil de `build.sh` pour calculer le K de même clarté que chaque gris.

Sans profil, `build.sh` s'arrête avec un message explicite : rien n'est produit à moitié.
