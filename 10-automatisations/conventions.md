# Conventions de conception des workflows n8n

Standards à appliquer à **tout** workflow créé ou modifié dans le cadre de ce copilot. Objectif : des workflows lisibles, fiables, maintenables — et exportables sans fuite de secrets.

---

## 1. Méthode de travail en 5 phases

Ne jamais implémenter directement un workflow non trivial. Toujours dérouler :

1. **Conseil** — comprendre le besoin réel, chercher des workflows ou templates similaires existants, challenger l'approche avec 2-3 alternatives concrètes (« ce pattern fait X de cette façon, as-tu envisagé Y ? »).
2. **Plan** — identifier le pattern adapté, lister les nodes, les interfaces, les cas d'erreur ; produire un plan écrit.
3. **Validation** — faire valider le plan par l'humain avant toute exécution.
4. **Exécution** — implémenter (via `n8n-mcp` de préférence), tester avec des données réalistes, vérifier l'état du workflow avant de considérer la tâche terminée.
5. **Capitalisation (REX)** — après mise en production, documenter les erreurs rencontrées, les corrections et les décisions d'architecture dans un REX (`rex-template.md`). C'est ce qui rend chaque implémentation suivante meilleure.

---

## 2. Architecture par défaut

```
Trigger → Validation (input) → Traitement → Sortie → Error Handler
```

- **Trigger** : webhook, cron ou événement — toujours nommé explicitement.
- **Validation** : vérifier structure et champs requis de l'input AVANT tout traitement. Rejeter tôt, avec un message explicite.
- **Traitement** : logique métier, appels API, transformations.
- **Sortie** : réponse, stockage, notification.
- **Error Handler** : l'error workflow global (`{{ERROR_WORKFLOW_ID}}`) assigné dans *Settings → Error workflow* de chaque workflow.

### Modularité — sub-workflows

- Découper les workflows complexes via `Execute Sub-workflow`. **Un workflow = une seule responsabilité.**
- **Maximum 4-6 nodes principaux** dans le workflow parent : abstraire le reste en sub-workflows réutilisables.
- Définir des **interfaces explicites** (inputs/outputs documentés) pour chaque sub-workflow.
- Attention : les sub-workflows n'héritent pas toujours du contexte (variables d'environnement, données du parent) — passer explicitement ce dont ils ont besoin en input.

### Versioning

- Dupliquer le workflow avant toute modification significative (`Mon-Workflow_v2`).
- Exporter les JSON (sanitisés) dans `workflows/` pour le contrôle de version Git.
- Ne jamais modifier un workflow de production directement : copier → tester → valider → déployer.

---

## 3. Nommage

### Workflows

- Format : `[Domaine] - [Action] - [Cible]`
- Exemples : `Intel - Analyser - Transcriptions meetings`, `Content - Veille - Hebdo`, `Reporting - Envoyer - Rapport quotidien`, `Error Handler - Notifier - Erreurs workflows`

### Nodes

- Jamais le nom par défaut. Format `Verbe + Objet` : `Valider payload`, `Récupérer métriques`, `Envoyer notification`.
- Préfixer les nodes de la branche d'erreur : `[Erreur] Notifier admin`.

### Variables et expressions

- Variables en `camelCase`.
- Toute expression complexe est documentée par une sticky note à côté du node.

---

## 4. Programmation défensive

Les services externes **vont** échouer et les LLM **vont** renvoyer des formats inattendus. Concevoir en conséquence :

- **`toArray()` systématique** sur les outputs LLM — un LLM renvoie parfois une string là où on attend un array :

  ```javascript
  const toArray = (v) => Array.isArray(v) ? v : (typeof v === 'string' && v ? [v] : []);
  ```

- **`alwaysOutputData: true`** sur tout node de recherche qui alimente un IF : sinon, 0 résultat = flux bloqué silencieusement.
- **`retryOnFail`** (au moins 1 retry avec délai) sur tous les nodes HTTP/API susceptibles de timeout.
- **`continueOnFail` / `onError` + node IF** pour le pattern try/catch : router les échecs vers une branche dédiée (log, alerte, retry paramétré différemment).
- **Erreurs explicites** : dans les Code nodes, `throw new Error("Champ 'transcript' manquant dans le payload webhook")` plutôt qu'un échec silencieux ou un output vide.
- **Valider les inputs en amont** : format email, dates valides, champs requis non vides, rejet des événements trop anciens, déduplication par event ID si le workflow peut être rejoué.
- **Ne jamais faire confiance aux valeurs par défaut des nodes** : configurer explicitement tous les paramètres importants (cause n°1 d'échecs runtime).
- **Appels LLM longs** : préférer un HTTP Request direct vers l'API (avec `responseMimeType: 'application/json'` chez Google, `response_format` ailleurs) aux nodes LangChain, qui peuvent tronquer silencieusement les prompts longs.

---

## 5. Performance

- **Batch processing** : `Split In Batches` par groupes de 50-100 pour les gros volumes.
- **Filtres le plus tôt possible** dans le flux.
- **Webhooks > polling** quand l'outil source le permet.
- **Ne pas sur-trigger** : aligner la fréquence des crons sur le besoin métier réel.

---

## 6. Sécurité

- **Jamais de secrets en clair** : clés API, tokens, mots de passe → credentials n8n (vault chiffré) uniquement.
- **Jamais de secrets dans les exports** : les JSON committés ne contiennent que des placeholders `{{...}}`.
- **Ne pas logger de données sensibles** ; masquer les champs sensibles.
- **Webhooks en production** : chemin non devinable + authentification si possible.
- **Moindre privilège** sur tous les scopes d'intégration.

---

## 7. Checklist qualité — avant activation

### Design
- [ ] Chaque node nommé explicitement
- [ ] Sticky notes sur la logique non évidente et les prompts
- [ ] Découpé en sub-workflows si > 6 nodes principaux
- [ ] Description du workflow renseignée

### Fiabilité
- [ ] Error workflow assigné (`{{ERROR_WORKFLOW_ID}}`)
- [ ] Retry policy sur les nodes HTTP/API
- [ ] `continueOnFail`/`onError` + routage IF sur les nodes risqués
- [ ] Validation des inputs en entrée
- [ ] `alwaysOutputData` sur les recherches alimentant un IF
- [ ] Idempotence vérifiée si rejouable (déduplication, upsert)
- [ ] Timeout configuré sur les nodes HTTP longs

### Performance
- [ ] Batching pour les gros volumes
- [ ] Filtres placés tôt

### Sécurité
- [ ] Aucun secret en dur — credentials vault uniquement
- [ ] Export sanitisé si committé

### Déploiement
- [ ] Testé avec des données réelles ou réalistes
- [ ] Version précédente sauvegardée
- [ ] Workflow **désactivé par défaut** jusqu'à validation finale
- [ ] REX rédigé après mise en production (`rex-template.md`)

---

## 8. Référence rapide — expressions n8n

| Expression | Description |
|---|---|
| `{{ $json.champ }}` | Champ de l'item courant |
| `{{ $('Nom du node').first().json.prop }}` | Premier item d'un autre node |
| `{{ $('Nom du node').item.json.valeur }}` | Item courant dans une boucle |
| `{{ $now.toFormat("yyyy-MM-dd") }}` | Date formatée |
| `{{ $workflow.id }}` / `{{ $execution.id }}` | IDs workflow / exécution |

Règle : une transformation qui tient en **une ligne sans boucle** → expression ; multi-étapes ou logique → Code node ; opération couverte par un node natif → node natif plutôt que Code.
