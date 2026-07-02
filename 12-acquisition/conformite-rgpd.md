# Conformité RGPD — prospection B2B automatisée

> Ce document résume le cadre applicable en France/UE. Il ne constitue pas un conseil juridique : en cas de doute (secteur régulé, volumes importants, données sensibles), consultez un professionnel.

## Base légale

La prospection B2B par email repose en France sur l'**intérêt légitime** (position CNIL) à trois conditions cumulatives :
1. **Pertinence du ciblage** : le message est en rapport avec la fonction professionnelle du destinataire (on n'écrit pas à un DAF pour vendre du design graphique).
2. **Information** : le destinataire sait d'où viennent ses données et peut l'apprendre facilement (mention d'information dans le message ou en un clic).
3. **Opposition** : un moyen simple et fonctionnel de s'opposer aux envois, dans chaque message. C'est géré techniquement par la plateforme (Lemlist/Salesforge), mais vérifiez que le lien est bien présent dans vos séquences.

La prospection vers des adresses **génériques** (contact@, info@) n'est pas soumise aux mêmes contraintes que les adresses nominatives, mais les conditions de pertinence restent de bonne pratique.

## Obligations pratiques dans ce module

- **Source des données traçable** : pour chaque liste (skill `scraping`, export d'un outil de sourcing), notez la source et la date de collecte dans la fiche campagne (`campagnes/`). Pas de harvesting sauvage : respectez les CGU des plateformes sources.
- **Minimisation** : ne collectez que ce qui sert la campagne (nom, fonction, entreprise, email pro). Pas de données personnelles hors sujet.
- **Aucune donnée personnelle versionnée** : les listes vivent dans la plateforme d'outreach ou en local non commité — jamais dans le repo Git.
- **Durée** : purgez les listes des non-répondants après la campagne ; un contact opposé ne doit jamais être réimporté.
- **LinkedIn** : les actions automatisées (connexions, messages) sont encadrées par les CGU de LinkedIn — restez dans les volumes gérés par la plateforme, qui les calibre pour ça.

## Rôle de la relecture humaine

Le copilot prépare (ciblage, listes, séquences) ; **un humain valide et lance**. La relecture vérifie : pertinence cible/message, présence de la mention d'information et de l'opt-out, véracité des claims (règle « aucun claim sans source » de `01-brand/`), volumes raisonnables.

## En cas de demande d'un prospect

- **Opposition/désinscription** : effective immédiatement (plateforme) + retrait des listes locales.
- **Demande d'accès ou de suppression** : répondez sous un mois ; supprimez de la plateforme ET de toute liste locale.
