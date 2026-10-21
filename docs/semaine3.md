# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Modèle renommé, `uvicorn api.main:app` s'arrête aussitôt sur `FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py`, puis `Application startup failed. Exiting.` : la panne est visible au moment même du lancement, avec la commande qui la répare. Une API qui démarrerait quand même paraîtrait en marche (le processus tourne, le port répond) et ne servirait que des 503 : on ne découvrirait le problème qu'à la première requête d'un utilisateur. Le 503 reste utile pour l'autre cas, celui où le modèle disparaît alors que l'API tourne déjà (`_classifier()` dans `api/main.py`).

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Non, les deux contrôles n'attrapent pas les mêmes textes. `{"text": ""}` est refusé par Pydantic (`min_length=1`) avec un 422 dont `detail` est une liste (`string_too_short`, `loc: ["body", "text"]`) ; `{"text": "   "}` passe Pydantic, puisqu'il a trois caractères, et c'est `predict()` qui le refuse, avec un 422 dont `detail` est la simple chaîne `"texte vide"`. Le second contrôle protège aussi `predict()` quand elle est appelée sans l'API (interface, scripts). Le défaut observé est ailleurs : le même refus arrive sous deux formes différentes, ce qu'un client de l'API doit gérer deux fois.
