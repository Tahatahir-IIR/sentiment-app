"""Évalue le modèle enregistré sur le même jeu de test qu'à l'entraînement.

Affiche la matrice de confusion et chaque avis mal classé, pour comprendre
pourquoi le modèle se trompe, pas seulement combien.

Usage : python src/evaluate.py
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from donnees import DEMO, RACINE, charger, decouper  # noqa: E402

MODELE = RACINE / "models" / "sentiment.joblib"
METRIQUES = RACINE / "models" / "metrics.json"
CLASSES = ["negative", "positive"]
MAX_AFFICHES = 15


def main() -> int:
    if not MODELE.exists() or not METRIQUES.exists():
        print("Modèle ou mesure absents : lancez d'abord python src/train.py")
        return 1
    source = json.loads(METRIQUES.read_text(encoding="utf-8"))["source"]
    pipeline = joblib.load(MODELE)
    _, X_test, _, y_test = decouper(charger(source))
    y_pred = pipeline.predict(X_test)

    print(f"Source : {source}, {len(X_test)} avis de test\n")
    print(classification_report(y_test, y_pred, digits=3))
    print("Matrice de confusion (lignes = vérité, colonnes = prédiction) :")
    matrice = confusion_matrix(y_test, y_pred, labels=CLASSES)
    print(pd.DataFrame(matrice, index=CLASSES, columns=CLASSES).to_string())

    erreurs = pd.DataFrame({"review": X_test, "verite": y_test, "prediction": y_pred})
    erreurs = erreurs[erreurs.verite != erreurs.prediction]
    if source == "demo" and DEMO.exists():
        types = pd.read_csv(DEMO)["type"]
        erreurs["type"] = types.loc[erreurs.index].values
    print(f"\n{len(erreurs)} erreurs sur {len(X_test)}")
    if "type" in erreurs:
        print("Par type d'avis : " + ", ".join(f"{t} {n}" for t, n in erreurs["type"].value_counts().items()))
    for _, e in erreurs.head(MAX_AFFICHES).iterrows():
        print(f"\n  vérité {e.verite}, prédit {e.prediction}")
        print(f"  {e.review[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
