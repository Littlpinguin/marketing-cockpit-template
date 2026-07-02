# {{NOM_DU_WORKFLOW}} — Design & plan d'implémentation

> Copier en `AAAA-MM-JJ-<slug>-plan.md` (et, pour les gros workflows, séparer la partie 1 dans un `-design.md` dédié). Le design se valide AVANT d'écrire le plan ; le plan s'exécute tâche par tâche. Voir `README.md`.

---

# Partie 1 — Design spec

**Date** : {{AAAA-MM-JJ}}
**Source d'inspiration** : {{template(s) des bibliothèques ou référence externe ayant inspiré l'architecture — voir ../bibliotheques.md}}
**Stack** : {{ex : LLM via HTTP Request direct, Google Sheets, SMTP…}}

## Objectif

Ce que le workflow doit produire, pour qui, à quelle fréquence. 3-6 lignes. Si plusieurs volets (nouveau workflow + modification d'un existant), les lister.

## Déclencheur

{{Webhook / Schedule (cron précis) / événement — et pourquoi ce choix}}

## Architecture

```
Trigger ({{détail}})
  → Valider input
  → {{Étape de traitement 1}}
  → {{Étape de traitement 2}}
  → {{Sortie : stockage / notification / réponse}}
  → Error Handler ({{ERROR_WORKFLOW_ID}})
```

Schéma ASCII du flux complet, avec les branches parallèles et les IF. C'est la vue que l'humain valide.

## Données & interfaces

- **Entrée attendue** : structure exacte (payload webhook, colonnes de la source…)
- **Sortie produite** : structure exacte (colonnes de la Sheet, format de la note, corps de l'email…)
- **Prompts IA** : objectif, règles, format de sortie JSON attendu (le prompt complet peut vivre dans le plan)

## Error handling

- Error workflow assigné : `{{ERROR_WORKFLOW_ID}}`
- Retry sur les appels externes ({{x2, 3s}})
- `continueOnFail` / `onError` sur : {{nodes non critiques}}
- Comportement en cas d'échec partiel : {{reprise automatique au prochain run ? déduplication ?}}

## Credentials réutilisés

| Credential | Usage |
|---|---|
| {{SMTP / OAuth2 / API LLM…}} | {{quels nodes}} |

*(Ne jamais copier d'ID de credential dans un document versionné public — dans un fork privé, les IDs facilitent l'implémentation.)*

## Décisions d'architecture

| Décision | Raison |
|---|---|
| {{Choix retenu}} | {{Pourquoi, et quelle alternative a été écartée}} |

## Alternatives écartées

- {{Approche B}} : écartée parce que {{raison}}
- {{Approche C}} : écartée parce que {{raison}}

---

# Partie 2 — Plan d'implémentation

> **Pour l'exécutant (Claude ou humain) :** dérouler tâche par tâche, dans l'ordre. Vérifier la structure du workflow après chaque tâche (`n8n_get_workflow` mode structure). Ne pas passer à la tâche suivante si la vérification échoue.

**Goal** : {{une phrase — le résultat final vérifiable}}
**Architecture** : {{résumé en 2-3 lignes du design validé ci-dessus}}
**Tech stack** : {{n8n (MCP), APIs utilisées}}

## Contexte clé pour l'implémenteur

Tout ce dont l'exécutant a besoin sans chercher ailleurs :

### Ressources existantes

- {{IDs de documents / Sheets / dossiers / workflows liés (error handler, sub-workflows)}}

### Patterns à suivre (REX)

- {{Leçons des REX applicables — ex : LLM en HTTP Request direct + JSON forcé ; alwaysOutputData sur les recherches → IF ; branches parallèles après les nodes d'action…}}
- Relire la table « Patterns d'erreurs connus » de `../conventions.md`

---

### Task 1 : {{Prérequis hors n8n}}

**Objectif :** {{ex : créer la Sheet de stockage, le label, le dossier}}

**Step 1 : {{action}}**

{{Détail exécutable : quoi créer, où, avec quelles colonnes/champs exacts}}

**Step 2 : Noter les IDs**

Conserver les IDs créés pour les tâches suivantes.

---

### Task 2 : {{Créer le workflow — trigger + premiers nodes}}

**Objectif :** {{sous-ensemble vérifiable}}

**Step 1 : Créer le workflow via `n8n_create_workflow`**

Nom : `{{[Domaine] - [Action] - [Cible]}}`
Settings : `executionOrder: "v1"`, `errorWorkflow: "{{ERROR_WORKFLOW_ID}}"`

Nodes :

1. **{{Nom du node}}** (`{{type}}` v{{X.Y}})
   - Position : [{{x}}, {{y}}]
   - {{Paramètres exacts, un par ligne}}
   - Credentials : {{lequel}}

2. **{{Nom du node}}** (`{{type}}` v{{X.Y}})
   - {{…}}

Connexions : 1 → 2 → …

**Step 2 : Vérifier via `n8n_get_workflow` mode structure**

---

### Task 3 : {{Traitement / IA}}

**Objectif :** {{…}}

**Step 1 : {{node Code — inclure le code complet}}**

```javascript
// Code node complet, prêt à coller — parsing défensif (toArray, throw explicites)
```

**Step 2 : {{node HTTP / natif — paramètres exacts, retry, timeout}}**

---

### Task 4 : {{Sortie + branches parallèles}}

**Objectif :** {{…}}

{{Nodes de sortie. Rappel : les nodes d'action qui écrasent $json (Gmail addLabels, markAsRead, send…) se branchent en PARALLÈLE depuis le dernier node porteur des données, pas en chaîne.}}

---

### Task 5 : Sticky notes + validation

**Step 1 :** Ajouter les sticky notes de documentation (une par zone logique : recherche, traitement IA, sauvegarde).

**Step 2 :** `validate_node` (minimal puis full) sur les nodes critiques, puis `validate_workflow`.

**Step 3 :** Dérouler la checklist qualité de `../conventions.md`.

---

### Task 6 : Test E2E + capitalisation

**Step 1 : Test avec données réalistes**

- {{Préparer le cas de test (email de test, payload webhook d'exemple…)}}
- Exécuter manuellement, vérifier chaque sortie attendue
- Le workflow reste **désactivé** jusqu'à validation humaine

**Step 2 : Activation**

Uniquement après validation explicite de l'humain.

**Step 3 : Capitalisation**

- Exporter le JSON dans `../workflows/{{slug}}.json` (sanitisé si le fork est partagé)
- Rédiger le REX : `../docs/rex-{{slug}}.md` (format `../rex-template.md`)
- Commit sur la branche `feat/{{slug}}`, merge après validation, tag si mise en production
