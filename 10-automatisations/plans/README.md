# plans/ — designs et plans d'implémentation des workflows

Ce dossier matérialise les phases **2 (Plan)** et **3 (Validation)** de la méthode (`../conventions.md`). Aucun workflow non trivial ne se construit sans un plan écrit et validé par l'humain — c'est ce qui distingue une automatisation fiable d'un bricolage.

## La méthode des plans

Pour chaque workflow, **deux documents** datés :

| Document | Nom de fichier | Contenu | Quand |
|---|---|---|---|
| **Design spec** | `AAAA-MM-JJ-<slug>-design.md` | Le *quoi* et le *pourquoi* : objectif, architecture (schéma ASCII des nodes), décisions d'architecture argumentées, error handling, credentials réutilisés | Phase conseil → plan |
| **Plan d'implémentation** | `AAAA-MM-JJ-<slug>-plan.md` | Le *comment* : contexte clé pour l'implémenteur, tâches numérotées avec steps détaillés (node par node : type, version, position, paramètres), test E2E, capitalisation | Après validation du design |

Pour les petits workflows, les deux parties peuvent tenir dans un seul fichier `-plan.md` — le template ci-dessous contient les deux.

## Cycle de vie

1. **Rédiger le design** à partir du besoin + des templates trouvés dans les bibliothèques (`../bibliotheques.md`). Y consigner les alternatives écartées.
2. **Faire valider le design par l'humain.** Pas d'implémentation avant.
3. **Dériver le plan** : tâches numérotées, chacune exécutable et vérifiable indépendamment. Y injecter le « contexte clé pour l'implémenteur » : credentials existants, ressources, patterns REX à suivre.
4. **Exécuter le plan tâche par tâche** via `n8n-mcp`, en vérifiant la structure du workflow après chaque tâche (`n8n_get_workflow`).
5. **Clore** : test E2E, export JSON sanitisé dans `../workflows/`, REX (`../rex-template.md`).

Le plan est un document d'exécution : un agent (ou vous-même dans 6 mois) doit pouvoir le dérouler sans aucune autre source d'information.

## Template

Copier `plan-template.md` :

```bash
cp plan-template.md "$(date +%F)-mon-workflow-plan.md"
```

## Pourquoi ça marche

- **Le design fige les décisions** avant qu'elles ne soient diluées dans les détails d'implémentation — le tableau « Décisions d'architecture » évite de re-débattre à chaque maintenance.
- **Les tâches numérotées bornent l'exécution** — chaque tâche a un objectif vérifiable, on sait toujours où on en est.
- **Le contexte pour l'implémenteur évite les allers-retours** — credentials, IDs de ressources et patterns connus sont listés une fois, au début.
- **Les plans archivés sont une mémoire** — avant un nouveau workflow, relire les plans similaires (et les REX) accélère la conception.
