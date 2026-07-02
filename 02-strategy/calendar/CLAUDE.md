# 02-strategy/calendar — calendrier éditorial central

## Rôle

`calendar.md` est la **colonne vertébrale** du copilot : tout contenu planifié, en cours ou publié y a une entrée. C'est le fichier que consultent tous les rôles avant de produire, et que met à jour toute skill qui fait avancer un livrable.

## Qui écrit quoi

| Acteur | Action |
|---|---|
| Module `veille` (00-intel, automatisations) | Verse des idées avec statut `idée` |
| `02-strategy` (planification mensuelle) | Transforme les idées retenues en entrées datées |
| Skills de production (social, email, seo, video…) | Créent le livrable, passent le statut à `brouillon` puis `à-valider`, renseignent le lien livrable |
| Validation client | Se fait via l'espace client (module `espace-client`, partage FTP) → statut `validé` |
| Publication (manuelle ou Postiz) | Passe le statut à `publié`, renseigne l'UTM final |

## Cycle de vie d'une entrée (statuts)

```
idée → brouillon → à-valider → validé → publié
```

- Jamais de saut de statut sans trace : qui a validé, quand.
- Une entrée `à-valider` depuis plus de 7 jours doit être relancée (module `automatisations`).

## Structure d'une entrée

Chaque entrée vit sous sa semaine dans `calendar.md` et contient : **date, canal, sujet, pilier, statut, lien livrable, UTM**. Voir le template dans `calendar.md`.

## Règles

1. **Consulter avant de créer.** Toute proposition de contenu commence par une lecture du calendrier (anti-doublon, équilibre des piliers).
2. **Mettre à jour au fil de l'eau.** Une skill qui écrit un draft met à jour le statut dans le même tour.
3. **Une entrée = un livrable = un canal.** Une vague multi-canal (blog → newsletter → LinkedIn) = plusieurs entrées liées au même sujet.
4. **UTM systématique** pour tout lien sortant publié : `utm_source`, `utm_medium`, `utm_campaign` cohérents avec `../kpi-framework.md`.
