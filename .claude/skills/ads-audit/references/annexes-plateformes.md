# Annexes plateformes secondaires — TikTok, Microsoft, Apple, Amazon

> Condensé depuis claude-ads v1.7.1 (AgriciDaniel, MIT) — voir `docs/vendored-content.md`. Grilles complètes d'origine : 28 checks TikTok, 24 Microsoft, ~25 Apple, ~30 Amazon. Ne charger ce fichier que si le compte audité utilise l'une de ces plateformes.

## TikTok Ads (créa d'abord — 30 % du score)

- **Créa** : ≥ 6 créas par ad group [Critique] ; 100 % vertical 9:16 1080×1920 [Critique] ; rendu natif/UGC, pas corporate ; hook en 1-2 s ; safe zone X:40-940, Y:150-1470 ; son toujours actif (93 % de la consommation est sound-on) ; Spark Ads testées (~3 % CTR vs ~2 % standard) ; aucune créa > 7 jours avec CTR en baisse.
- **Technique (25 %)** : Pixel + Events API avec passback `ttclid` ; événements standard ; advanced matching.
- **Enchères (20 %)** : Lowest Cost pour le volume, Cost Cap pour l'efficacité ; budget quotidien ≥ 50× CPA cible par ad group ; learning = ≥ 50 conversions / 7 j ; ne rien éditer pendant le learning (reset).
- **Structure (15 %)** : prospection / retargeting séparés ; Smart+ testé ; Search Ads Toggle activé (+20 % de conversions combiné à l'In-Feed).
- **Seuils** : CTR in-feed ≥ 1,0 % ; watch time moyen ≥ 6 s ; kill rule 3× CPA.

## Microsoft (Bing) Ads

- **Technique** : tag UET partout ; enhanced conversions ; **import Google validé manuellement** (URLs, extensions, enchères — baisser les bids de 20-35 %, avantage CPC —, objectifs de conversion recréés nativement). ⚠️ Les imports planifiés peuvent réactiver des campagnes en pause : les désactiver après le setup initial.
- **Spécificités à exploiter** : ciblage par profil LinkedIn (unique, précieux en B2B) ; Multimedia Ads ; Action Extensions ; placement Copilot pour PMax.
- **Volumétrie** : budget typique 20-30 % du budget Google ; CPC attendu 20-40 % plus bas ; CVR comparable à Google (FAIL si > 50 % plus bas) ; Audience Network OFF sauf test isolé.

## Apple Ads (apps iOS uniquement)

- **Structure** : campagnes séparées Brand / Concurrents / Catégorie / Search Match (découverte) — **jamais Search Match et Exact dans le même ad group** ; promouvoir les requêtes gagnantes du Search Match vers l'Exact.
- **Enchères** : TTR benchmark > 2,5 % (Search Results) ; CR tap→install 50-65 % en brand, 20-40 % en catégorie ; bids différenciés par match type et par mot-clé ; Maximize Conversions (GA fév. 2026) n'optimise que l'install, pas le post-install.
- **Custom Product Pages** : ≥ 3 variantes par type de campagne, assets alignés sur les thèmes de mots-clés (+6-8 % de CR) ; 78 % du volume de recherche App Store vient d'appareils avec la personnalisation désactivée → cibler par la créa, pas par la démographie.
- **Attribution** : MMP (AppsFlyer/Adjust/Branch/Singular) connecté via AdAttributionKit + ATT ; événements post-install remontés vers Apple Ads.

## Amazon Ads (vendeurs marketplace uniquement)

- **Harvesting (25 % — le cœur)** : cadence hebdo/bimensuelle Auto → Manual (promouvoir les termes convertisseurs en Exact) ; négatifs systématiques dans les campagnes Auto pour éviter la cannibalisation ; brand defense isolée.
- **ACOS/TACOS (20 %)** : cibles ACOS par portefeuille selon la marge de contribution ; TACOS en baisse trimestre après trimestre ; day-parting si les données le justifient.
- **Structure** : ≥ 1 campagne Auto par ASIN prioritaire ; portefeuilles par étape de funnel ; Sponsored Brands (logo + 3 produits, vidéo 15-30 s avec hook < 2 s et sous-titres) ; Sponsored Display en Audience et Contextuel séparés.
- **Enchères** : Up and Down pour l'Exact convertisseur ; multiplicateurs top-of-search pilotés ; pas de campagne plafonnée < 2× le budget quotidien courant.
- **Brand Analytics** (Brand Registry) : Top Search Terms pour les gaps de share-of-voice ; Amazon Attribution si trafic externe.
