# Calendrier éditorial — {{COMPANY_NAME}}

> Colonne vertébrale du copilot. Statuts : `idée` → `brouillon` → `à-valider` → `validé` → `publié`.
> Une entrée = un livrable = un canal. Voir `CLAUDE.md` de ce dossier pour les règles.

## Backlog d'idées (non datées)

| Sujet | Pilier | Canal pressenti | Source de l'idée | Statut |
|---|---|---|---|---|
| {{EXEMPLE_SUJET_BACKLOG}} | {{PILLAR_1}} | linkedin | veille / meeting / brainstorm | idée |

---

## Semaine du {{DATE_LUNDI_ISO}} (S{{NUMERO_SEMAINE}})

| Date | Canal | Sujet | Pilier | Statut | Livrable | UTM |
|---|---|---|---|---|---|---|
| {{DATE_ISO}} | linkedin | {{SUJET}} | {{PILIER}} | idée | — | — |
| {{DATE_ISO}} | newsletter | {{SUJET}} | {{PILIER}} | brouillon | `04-email/newsletter/drafts/{{SLUG}}.md` | — |
| {{DATE_ISO}} | blog | {{SUJET}} | {{PILIER}} | à-valider | `09-seo/articles/{{SLUG}}.md` | — |
| {{DATE_ISO}} | video | {{SUJET}} | {{PILIER}} | validé | `08-video/scripts/{{SLUG}}.md` | — |
| {{DATE_ISO}} | linkedin | {{SUJET}} | {{PILIER}} | publié | `03-social-media/linkedin/examples/{{SLUG}}.md` | `utm_source=linkedin&utm_medium=social&utm_campaign={{CAMPAGNE}}` |

## Semaine du {{DATE_LUNDI_ISO_S1}} (S{{NUMERO_SEMAINE_S1}})

| Date | Canal | Sujet | Pilier | Statut | Livrable | UTM |
|---|---|---|---|---|---|---|
| | | | | | | |

---

## Conventions

- **Date** : ISO `AAAA-MM-JJ` (date de publication visée).
- **Canal** : `linkedin`, `newsletter`, `blog`, `video`, `discord`, `whatsapp`, `event`, `web`.
- **Pilier** : un des piliers définis dans `../content-pillars.md`.
- **Livrable** : chemin relatif repo vers le fichier, dès le statut `brouillon`.
- **UTM** : renseigné au passage à `publié` (`utm_source=<canal>&utm_medium=<type>&utm_campaign=<campagne>`).
- Archiver les semaines de plus de 2 mois en bas de fichier ou dans `archive-{{ANNEE}}.md`.
