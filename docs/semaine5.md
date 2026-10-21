# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

Parce que tout ce que l'API garantit depuis le TP4 serait alors contourné : le refus des textes faits de blancs (schéma), l'abstention sous 0,60 et la correspondance des étiquettes vivent dans `api/`, pas dans `predict()`. Appelée directement, `predict()` renverrait `negative` à 0,5162 pour « xqzvb wlkptr grombu », là où l'interface, passant par l'API, affiche « Je ne sais pas ». Et un modèle réentraîné ne demande qu'un redémarrage de l'API : la page n'a aucune ligne à changer, puisqu'elle ne connaît que `POST /predict` et `GET /health` (`ui/client.py`).

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Pour « xqzvb wlkptr grombu », la page affiche « Je ne sais pas : à faire vérifier par un humain » avec 52 %, puis l'encadré « La confiance est sous le seuil d'abstention : un humain doit trancher. » Un verdict forcé aurait affiché « Avis négatif » : l'agent l'aurait cru, alors que le modèle ne reconnaît aucun mot de ce texte et ne fait que répéter son ordonnée à l'origine. L'abstention dit à l'utilisateur quoi faire de l'avis, et garde la confiance visible pour qu'il sache pourquoi.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

API arrêtée, la page s'ouvre quand même et affiche en rouge, tout en haut, « API injoignable : lancez d'abord uvicorn api.main:app » ; chaque analyse redonne ce même message au lieu d'une trace d'erreur Python. Si l'API tourne sans modèle, le message devient « Modèle non chargé : python src/train.py, puis relancer l'API. », et un texte fait d'espaces reçoit l'avertissement « Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères. »

Sur les 6 avis de `data/avis_exemple.csv`, un seul part vers un humain : « xqzvb wlkptr grombu » (52 %). Les cinq autres reçoivent un verdict franc, 3 positifs et 2 négatifs, avec des confiances de 62 % à 80 % ; « Pas déçu du tout, je recommande » est classé positif à 62 %, juste au-dessus du seuil.
