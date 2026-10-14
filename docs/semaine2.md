# Semaine 2 : analyse des erreurs du modèle

Sur le jeu de démonstration, le modèle se trompe sur 8 avis de test sur 58 (F1 macro 0,862), dont 5 avis négatifs classés positifs, l'erreur qui compte puisqu'un client mécontent est alors traité en retard ; 6 des 8 erreurs portent sur des avis mitigés et 2 sur des avis neutres.

Ces erreurs viennent de la représentation en sac de mots : un avis « livraison rapide, mais finalement colis abîmé » et son inverse contiennent les mêmes mots, donc le même vecteur TF-IDF, alors que l'étiquette dépend de l'ordre, de la moitié qui conclut.

Pour les corriger, il faudrait une représentation qui tient compte de l'ordre (par exemple des plongements de phrase de type sentence-transformers) ou davantage d'avis mitigés étiquetés, et en attendant envoyer à un agent les avis dont la confiance est faible, ce que fera le seuil d'incertitude du TP3.

| | Démonstration | Allociné |
| --- | --- | --- |
| Avis | 290 | 20 000 |
| Entraînement / test | 232 / 58 | 16 000 / 4 000 |
| Vocabulaire | 460 termes | 149 529 termes |
| F1 macro (seuil 0,85) | 0,862 | 0,920 |
| Négatifs classés positifs | 5 sur 29 | 181 sur 2 041 |

Le modèle et ses réglages sont identiques dans les deux colonnes : seul le volume de données change, et la mesure sur 4 000 avis est bien plus crédible que celle sur 58.
