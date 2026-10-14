# Semaine 3 : choix du seuil d'incertitude

Mesuré sur les 4 000 avis de test Allociné (modèle F1 macro 0,920, 318 erreurs, dont 181 avis négatifs classés positifs) :

| Seuil | Avis envoyés à un agent | Erreurs restant automatiques | Négatifs manqués sans relecture |
| --- | --- | --- | --- |
| 0,50 | 0 (0 %) | 318 | 181 |
| 0,60 | 509 (12,7 %) | 126 | 74 |
| 0,70 | 1 183 (29,6 %) | 49 | 28 |
| 0,75 | 1 626 (40,6 %) | 27 | 17 |

Nous retenons le seuil de 0,60 : il envoie environ un avis sur huit à un agent et divise par 2,4 le nombre de clients mécontents traités en retard sans relecture (181 à 74).

Passer à 0,70 ferait encore tomber ces négatifs manqués à 28, mais au prix de près d'un avis sur trois relu à la main, ce qui retire l'essentiel de l'intérêt du tri automatique pour une équipe qui reçoit des milliers d'avis par jour ; le bon réglage se décide avec elle, selon le nombre d'agents disponibles.

Limite observée : le modèle est entraîné sur des critiques de films, et sur des avis de commerce en ligne il hésite même sur des cas nets (« Produit cassé à l'arrivée et service client injoignable » ne reçoit que 58 % de confiance, donc « à vérifier »), tandis qu'il classe négatif à 65 % un avis mitigé qui devrait être relu. Le seuil compense en partie ce décalage de domaine, mais seul un réentraînement sur des avis clients réels étiquetés le corrigerait.
