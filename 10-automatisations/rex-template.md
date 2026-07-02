# REX — {{NOM_DU_WORKFLOW}}

> **Format de capitalisation des leçons apprises.** Copier ce fichier dans `docs/rex-{{slug-du-workflow}}.md` après chaque mise en production ou incident significatif. Objectif : que chaque erreur rencontrée ne soit payée qu'une seule fois. Les REX accumulés deviennent la mémoire technique du module — Claude les lit avant de concevoir un nouveau workflow.

**Workflow ID** : `{{WORKFLOW_ID}}`
**Date** : {{AAAA-MM-JJ}}
**Statut** : Brouillon | En test | En production | Retiré

## Description

Ce que fait le workflow, en 3-6 lignes : déclencheur, étapes principales, sorties. Suffisamment précis pour qu'un lecteur qui n'a jamais ouvert le workflow comprenne son rôle dans le système.

## Erreurs rencontrées et corrections

> Une sous-section par erreur. La **leçon** est la partie la plus importante : c'est elle qui est réutilisable.

### 1. {{Titre court de l'erreur}}

**Problème** : ce qui ne fonctionnait pas, techniquement (node concerné, paramètre, comportement observé).

**Symptôme** : ce qu'on voyait de l'extérieur (résultat erroné, flux bloqué, hallucination du LLM, notification absente...). Utile pour reconnaître le même problème plus tard.

**Correction** : ce qui a été changé, précisément (paramètre, node ajouté, code).

**Leçon** : la règle générale à retenir, formulée pour être applicable à d'autres workflows. Si la leçon est vraiment générale, la reporter aussi dans `conventions.md`.

### 2. ...

## Décisions d'architecture

| Décision | Raison |
|---|---|
| {{Choix technique retenu}} | {{Pourquoi, et quelle alternative a été écartée}} |
| | |

## Points de vigilance pour la maintenance

- Dépendances externes à surveiller (credentials à renouveler, structure attendue d'un document source, dossier surveillé, quota API...)
- Hypothèses fragiles (format d'un payload webhook, champ optionnel côté source...)
- Ce qu'il faut vérifier avant toute modification future

## Métriques (optionnel)

- Fréquence d'exécution constatée :
- Taux d'erreur depuis la mise en production :
- Temps gagné estimé par exécution :

---

# Exemples de leçons (issues d'un système en production réelle)

> Trois entrées rédigées au format ci-dessus, tirées de REX réels (anonymisés). Elles montrent le niveau de précision attendu — et sont vraies : vous rencontrerez probablement ces trois problèmes. Supprimez cette section dans vos REX.

### Exemple 1 — Le node LangChain « Basic LLM Chain » perd les longs prompts

**Problème** : Malgré un texte source correct et complet confirmé en sortie du node précédent (~45 000 caractères), le node Basic LLM Chain ne transmettait pas le contenu intégral au modèle.

**Symptôme** : Le LLM « hallucinait » des analyses complètement fictives (entités inventées, participants fictifs), alors que les données d'entrée étaient valides. Aucune erreur levée — l'échec était silencieux.

**Correction** : Remplacement du LLM Chain + node modèle par 3 nodes : Code (construction du prompt) → HTTP Request (appel direct de l'API du LLM) → Code (parsing défensif de la réponse). Avec forçage du JSON en sortie (`responseMimeType: 'application/json'` chez Google, `response_format` ailleurs).

**Leçon** : Pour les prompts longs ou les cas critiques, préférer l'appel HTTP direct à l'API plutôt que les nodes LangChain de n8n : le contrôle est total sur ce qui est réellement envoyé. Règle reportée dans `conventions.md`.

### Exemple 2 — Identification échouée sur du texte transcrit (matching exact trop fragile)

**Problème** : Le workflow devait rattacher une transcription de réunion à une entité connue (liste dans une Sheet). La transcription vocale écrivait le nom phonétiquement (ex. « akmé solu.sion » pour une entité « Acme Solutions ») : le matching exact ne trouvait jamais rien.

**Symptôme** : Entité « non identifiée » malgré une transcription correcte et une entité bien présente dans la liste de référence.

**Correction** : Matching fuzzy dans un Code node — normalisation (minuscules, accents, caractères spéciaux) puis score de similarité avec seuil (~0,5) au lieu de l'égalité stricte.

**Leçon** : Les transcriptions vocales contiennent des erreurs phonétiques. Toute identification basée sur du texte transcrit (noms propres, entreprises) doit prévoir un matching fuzzy avec normalisation et seuil de similarité.

### Exemple 3 — Les nodes d'action écrasent les données du flux

**Problème** : Un node d'action (type Gmail `addLabels`) retourne la réponse de l'API (id, threadId, labels), pas les données d'entrée. Tous les nodes chaînés derrière perdaient les champs métier construits en amont.

**Symptôme** : Le node suivant échouait (« Invalid id value »), les colonnes du log étaient vides, et un IF en aval routait tout vers FALSE — trois symptômes différents pour une seule cause.

**Correction** : Restructuration en **branches parallèles** : toutes les étapes dépendant des données métier (labelliser, logger, marquer comme lu, IF) partent du dernier node porteur des données complètes, au lieu de se chaîner les unes derrière les autres.

**Leçon** : Les nodes d'action (envoi, labellisation, mise à jour) remplacent `$json` par leur propre réponse API. Ne jamais chaîner de node dépendant de données custom après un node d'action — brancher en parallèle depuis le dernier node qui contient tout.
