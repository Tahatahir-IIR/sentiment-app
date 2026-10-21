# Semaine 2 : analyse des erreurs du modèle

Sur le jeu de démonstration, le modèle se trompe sur 7 avis de test sur 58 (F1 macro 0,879) : 2 avis négatifs classés positifs, l'erreur qui compte puisqu'un client mécontent est alors traité en retard, et 5 avis positifs classés négatifs, tous des avis mitigés.

Ces erreurs viennent de la représentation en sac de mots : dans « Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé », les mots positifs et négatifs sont comptés sans tenir compte de leur ordre, alors que l'étiquette suit la seconde moitié, celle qui conclut.

Pour les corriger, il faudrait une représentation qui voit l'ordre ou la négation (n-grammes plus longs, plongements de phrase de type sentence-transformers) ou davantage d'avis mitigés étiquetés, et en attendant ne pas laisser le modèle trancher seul quand il hésite.

| | Démonstration | Allociné |
| --- | --- | --- |
| Avis | 290 | 20 000 |
| Entraînement / test | 232 / 58 | 16 000 / 4 000 |
| Vocabulaire | 316 termes | 149 529 termes |
| F1 macro (seuil 0,85) | 0,879 | 0,920 |

Le modèle et ses réglages sont identiques dans les deux colonnes : seul le volume de données change. Mais le modèle Allociné, appris sur des critiques de films, fait 18 erreurs sur les 58 avis de test du jeu de démonstration (contre 7 pour le modèle de démonstration) : un meilleur score sur son propre jeu ne garantit rien sur des avis clients d'un autre domaine.
