# sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et déploiement d'applications intelligentes* (A. Larhlimi).
Le besoin : une équipe relation client reçoit des milliers d'avis par jour et veut voir les **avis négatifs** en
tête de file. Le dépôt grandit chaque semaine ; rien n'est jeté.

| TP | Ce que le dépôt contient | Où | Compte rendu |
| --- | --- | --- | --- |
| TP1 | Environnement, structure, trois fiches de cadrage | `docs/cadrage/`, `scripts/` | les fiches |
| TP2 | Modèle TF-IDF et régression logistique, évaluation, métriques versionnées | `src/`, `models/metrics.json` | `docs/semaine2.md` |
| TP3 | API FastAPI : `GET /health`, `POST /predict` | `api/` | `docs/semaine3.md` |
| TP4 | Tests aux limites et d'intégration, abstention `INDETERMINE`, jeu d'or, ruff, mypy, pre-commit | `tests/`, `data/jeu_or.csv` | `docs/semaine4.md` |
| TP5 | Interface Streamlit, cliente de l'API | `ui/` | `docs/semaine5.md` |

État actuel : `98 passed, 1 xfailed`, couverture de `api/` à 100 %, `ruff` et `mypy` muets, CI verte.

## Installation

Python 3.11 (3.12 et 3.13 sont à éviter : pas de versions précompilées pour certains paquets).

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1          # Linux, macOS, Git Bash : source .venv/bin/activate
pip install pandas scikit-learn pytest "fastapi==0.115.*" "httpx==0.27.*" "uvicorn==0.30.*" "streamlit==1.39.*"
pip install -r requirements-dev.txt
pre-commit install                  # une fois par clone : ruff et mypy à chaque commit
python scripts/check_setup.py       # attendu : 0 erreur(s), 0 avertissement(s)
```

La première commande `pip install` reprend la liste de paquets de la CI. `pip install -r requirements.txt`
échoue pour l'instant : `pyarrow==21.0.*` n'est pas compatible avec `mlflow==2.17.*` (question posée à
l'enseignant). L'avertissement `streamlit 1.39.1 requires packaging<25` est sans conséquence.

## Entraîner le modèle

Le modèle (`models/sentiment.joblib`) n'est jamais commité : il se reconstruit en une commande.

```powershell
python src/make_demo.py             # 290 avis de démonstration, 145 par classe
python src/train.py                 # F1 macro 0,879 sur le jeu de démonstration (seuil 0,85)
python src/evaluate.py              # matrice de confusion et exemples d'erreurs
python src/train.py --allocine      # facultatif : 20 000 avis Allociné, F1 macro 0,920
```

L'API, les tests et la CI utilisent le modèle du jeu de démonstration : après un entraînement sur Allociné,
relancez `python src/train.py`.

## Lancer l'application

Deux programmes tournent en même temps, chacun dans son terminal, environnement virtuel activé.

```powershell
uvicorn api.main:app --reload       # l'API : http://localhost:8000/docs
streamlit run ui/app.py             # la page : http://localhost:8501
```

L'API refuse de démarrer sans modèle. Si le port 8000 est déjà pris, lancez l'API avec `--port 8001` et
indiquez-le à la page : `$env:API_URL = "http://127.0.0.1:8001"` avant `streamlit run`.

Ce que l'API renvoie :

| Requête | Réponse |
| --- | --- |
| `{"text": "Livraison rapide, produit conforme, très satisfait"}` | 200, `POSITIVE`, 0,777 |
| `{"text": "Produit cassé et service injoignable, à fuir"}` | 200, `NEGATIVE`, 0,7465 |
| `{"text": "xqzvb wlkptr grombu"}` | 200, `INDETERMINE`, 0,5162 (confiance sous le seuil de 0,60) |
| `{"text": ""}`, `{"text": "   "}`, `{}`, `{"text": 42}` | 422, `detail` sous la forme standard de FastAPI |
| modèle retiré ou en panne | 503 ou 500, sans message interne |

## Tests et qualité

```powershell
python -m pytest -q                                              # 98 passed, 1 xfailed
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
ruff check .
mypy api
python src/courbe_seuil.py          # compromis du seuil d'abstention
python src/bilan_jeu_or.py          # le jeu d'or : 10 justes, 9 abstentions, 1 erreur déclarée
```

Le `xfailed` est une erreur connue et déclarée du jeu d'or : une négation (« Je ne suis pas satisfait »)
que le sac de mots ne voit pas. Sans modèle sur le poste, les tests qui l'appellent sont ignorés.

| Fichier de tests | Ce qu'il vérifie |
| --- | --- |
| `test_environment.py`, `test_cadrage.py`, `test_git_history.py` | TP1 : environnement, fiches, deux auteurs de commits |
| `test_model.py` | TP2 : métriques versionnées, seuil de F1, `predict()` |
| `test_api.py` | TP3 : les réponses de l'API |
| `test_limites.py`, `test_integration.py`, `test_jeu_or.py` | TP4 : frontières du contrat, propriétés hypothesis, démarrage et pannes, jeu d'or |
| `test_client.py`, `test_interface.py` | TP5 : le client de l'API et la page Streamlit |

La CI (`.github/workflows/ci.yml`) rejoue à chaque push, sur une machine neuve : diagnostic, entraînement du
modèle de démonstration, ruff, mypy, puis les tests avec un seuil de couverture de 95 %.

## Structure

```text
sentiment-app/
├── README.md, TESTS.md, AIDE-GIT.md, DEPANNAGE.md, MARCHE-A-SUIVRE*.md, TP*-ENONCE.md
├── requirements.txt, requirements-dev.txt, pyproject.toml, pytest.ini, .pre-commit-config.yaml
├── .github/workflows/ci.yml   # intégration continue
├── src/                       # TP2 : make_demo, train, evaluate, predict ; TP4 : courbe_seuil, bilan_jeu_or
├── api/                       # TP3 : main (routes), schemas (contrat Pydantic), model (seuil, étiquettes)
├── ui/                        # TP5 : app (la page), client (les appels à l'API)
├── tests/                     # pytest, TP1 à TP5
├── data/                      # sample_reviews.csv, jeu_or.csv, avis_exemple.csv ; le reste est régénérable
├── models/                    # metrics.json seulement : le modèle n'est jamais commité
├── docs/                      # cadrage/ (fiches du TP1), semaine2.md à semaine5.md
├── scripts/                   # setup, diagnostic, création de fiche, clone de vérification
├── notebooks/                 # variantes Colab
└── exemples/                  # scripts d'aperçu fournis avec le TP1, non notés
```

Le dossier `app/`, prévu par le kit du TP1, est resté vide : l'API du TP3 vit dans `api/`.

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travail de la semaine 1 |
| --- | --- | --- | --- |
| Membre A | Taha Tahir | Tahatahir-IIR | |
| Membre B | KHALDOUN Soufiane | Soufiane205 | |
