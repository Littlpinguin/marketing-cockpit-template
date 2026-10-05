# Imprimés produits

Un sous-dossier par livrable. Dans le template, le contenu de ce dossier est ignoré par Git, comme tout contenu produit. Un fork qui veut versionner les **sources** de ses imprimés (maquette, contenus, scripts de build) retire les deux lignes `14-print/productions/` de son `.gitignore` ; les PDF et les rendus, eux, suivent leur source et ne sont jamais versionnés (`14-print/**/output/`, `14-print/**/*.pdf`). Un imprimé rattaché à un événement peut vivre dans le dossier de l'événement (`07-events/<événement>/`) : il suit alors la même structure.

## Structure d'une production

```
<slug>/
├── README.md                    # état, décisions, fiche imprimeur, pièges rencontrés
├── contenus/
│   ├── 00-faits-verifies.md     # tout chiffre, date, nom propre imprimé, avec source et date
│   └── textes.md                # textes validés, dans l'ordre du chemin de fer
├── maquette/
│   ├── pages.html               # la maquette, sur le gabarit de 14-print/gabarits/
│   ├── print.css                # le gabarit adapté au format
│   └── assets/                  # images aplaties, plaques, chiffres en PNG 600 dpi
├── build/                       # scripts propres au livrable (appellent 14-print/lib/)
└── output/                      # PDF -qa, -print, -complet : jamais versionnés
```

## Le README d'une production consigne

| Rubrique | Contenu |
|---|---|
| Fiche | format fini, reliure, nombre de pages, papier intérieur et couverture, finition, tirage |
| Imprimeur | produit configuré, fond perdu exigé, zone de sécurité, profil ICC et PDF/X exigés, nombre de fichiers et ordre des pages, contrôle des données demandé ou non |
| Calendrier | date de livraison souhaitée, délai de production et de transport, **date limite d'envoi** |
| Chemin de fer | une ligne par double page : gabarit, élément dominant, densité |
| Contrôles | dernière sortie OK de `verify.py` et `qa.py`, audits des agents, épreuve papier |
| Points ouverts | validations humaines attendues, avec le nom de la personne qui tranche |

Avant de démarrer un nouvel imprimé, ouvrir le README d'une production existante de même nature : ses pièges sont ceux du prochain.
