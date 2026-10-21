# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de VOS exécutions.

## 1. Couverture

- Avant (étape A) : 91 % pour `api/` (`main.py` à 86 %), lignes jamais exécutées : `main.py` 49, 77-79, 85-87.
- Pour chacune, le comportement qu'aucun test ne vérifiait :
  - ligne 49 : le 503 quand le modèle n'est pas chargé, aucun test ne retirait le modèle d'une API démarrée ;
  - lignes 77-79 : le 500 quand le modèle plante en pleine requête, aucun test ne provoquait de panne ;
  - lignes 85-87 : le lancement direct (`python api/main.py`), qui ne tourne jamais sous pytest.
- Après (étape D) : 100 % avec le bloc `if __name__ == "__main__":` exclu (`# pragma: no cover`), 97 % sans exclusion (les trois lignes 83-85 du lancement direct). C'est la seule exclusion : ce bloc démarre un vrai serveur uvicorn, ce qu'un test unitaire ne doit pas faire, et le démarrage réel est déjà vérifié par `test_demarrage_reel_charge_le_modele`.

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| --- | --- | --- |
| `{"text": "   "}` reçoit 422 mais avec `detail` en simple chaîne (`"texte vide"`, produite par `predict()` du TP2), alors que `{"text": ""}` reçoit la liste standard de Pydantic : deux formes pour le même refus, que l'interface du TP5 devrait traiter deux fois | `test_frontieres_du_contrat[espaces-seuls]` (forme du 422) | `field_validator` dans `api/schemas.py`, avec la règle de `predict()` : vide après `str.strip()` |
| Le caractère `'\x85'` (NEL, blanc Unicode) passe `min_length=1` mais `str.strip()` le retire : même défaut, sur un cas auquel personne n'avait pensé | `test_tout_texte_blanc_est_refuse_par_le_schema` (hypothesis, « Falsifying example: texte='\x85' ») | Même correction ; le cas est ajouté au test paramétré (`blanc-unicode-nel`) |
| Une panne `ValueError("bug interne")` du modèle répond 422, avec le message interne dans la réponse : l'API accuse le client d'une erreur du serveur et laisse fuir son fonctionnement | `test_modele_en_panne_500_sans_message_interne[ValueError]` | Conversion de `ValueError` en 422 retirée de `api/main.py` (le schéma garantit déjà un texte non vide) ; toute panne répond 500, `raise ... from None` |
| Un texte sans aucun mot connu (`"xqzvb wlkptr grombu"`) reçoit `NEGATIVE` à 0,5162, un verdict qui a l'air franc | `test_predict_mots_inventes_indetermine` | Abstention : sous `SEUIL_ABSTENTION = 0.60`, l'étiquette devient `INDETERMINE` |
| `.upper()` transforme n'importe quelle classe du modèle en étiquette : un modèle à trois classes aurait servi `NEUTRE`, hors contrat | mypy, une fois les étiquettes typées (`typeddict-item` sur `api/model.py`), puis `test_classes_inattendues_l_api_refuse_de_demarrer` | Correspondance explicite `positive → POSITIVE`, `negative → NEGATIVE`, vérifiée au démarrage : toute autre classe fait refuser le démarrage |

Le premier défaut répond aussi à la question B.3 : la forme liste vient de la validation Pydantic, la forme chaîne de `HTTPException(422, detail=str(e))` dans `main.py`. L'interface du TP5 préfère une seule forme : un seul code pour traduire tout refus en message clair.

## 3. Seuil d'abstention

- Texte inventé : `NEGATIVE`, 0,5162, pour trois textes différents. Sans mot connu, le vecteur TF-IDF est nul, le produit avec les poids vaut zéro, et il ne reste que l'ordonnée à l'origine de la régression logistique : la même probabilité pour tout texte inconnu, légèrement penchée vers la classe négative.
- Trois points de la courbe (`python src/courbe_seuil.py`, 58 avis de test du jeu de démonstration) :

| Seuil | Le modèle répond à | Exactitude sur ces avis | Erreurs | Vers un humain |
| --- | --- | --- | --- | --- |
| 0,50 | 58 (100 %) | 0,879 | 7 | 0 |
| 0,60 | 42 (72 %) | 0,952 | 2 | 16 |
| 0,70 | 37 (64 %) | 1,000 | 0 | 21 |

- Seuil retenu : 0,60 ; part des avis envoyés à un humain : 16 sur 58, soit 28 % ; justification : il évite 5 des 7 erreurs du modèle et laisse au modèle près des trois quarts des avis. Monter à 0,70 supprimerait les 2 dernières erreurs, mais au prix de 5 avis de plus à relire, et une exactitude de 1,000 mesurée sur 37 avis ne prouve pas grand-chose.

## 4. Jeu d'or

- Bilan (`python src/bilan_jeu_or.py`, 20 avis dont 8 difficiles) : justes 10, abstentions 9, erreurs franches déclarées 1, erreurs franches non déclarées 0.
- L'erreur déclarée : « Je ne suis pas satisfait, le produit ne fonctionne pas » reçoit `POSITIVE` à 0,67. Le sac de mots voit « satisfait » et ignore « ne pas » ; elle reste dans le jeu en `xfail(strict=True)`.
- Ce que ces chiffres disent du modèle : il ne se trompe franchement qu'une fois, mais il s'abstient beaucoup, y compris sur quatre avis faciles (« Commande reçue en deux jours, emballage soigné » à 0,52) dont les mots sont absents de ses 316 termes. Les avis ironiques, mitigés et d'un autre domaine finissent presque tous en abstention plutôt qu'en erreur : le seuil fait son travail, mais un modèle appris sur 232 avis sait trop peu de choses pour répondre seul à des avis réels.

## 5. Outils statiques

- Remarques au départ : ruff 11 (B904 deux fois dans `main.py`, I001 et F401 dans `model.py`, F401 et B905 deux fois dans `evaluate.py`, I001 dans `test_api.py`, E741 trois fois dans deux tests du TP1), mypy 0 (`Success: no issues found in 4 source files`).
- Parmi les cinq défauts de la partie 2, ruff n'en a signalé aucun : son B904 sur le `raise` du 422 touche la bonne ligne, mais pour une question de chaînage d'exceptions, pas pour le mauvais code de retour. mypy n'en a trouvé qu'un, et seulement après que nous avons typé les étiquettes : avec un `dict` sans précision, tout ce qui sort de `predict()` est `Any`, et mypy n'a rien à vérifier.
- Conclusion : les outils statiques attrapent ce qui se voit dans le texte du code (imports, noms, constructions risquées) et coûtent presque rien une fois branchés au crochet et à la CI ; les défauts de comportement, eux, n'apparaissent qu'en exécutant l'API à ses limites, et mypy ne vaut que ce que valent les types qu'on lui donne.
