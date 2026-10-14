"""Entraîne le classifieur de sentiment et versionne sa mesure.

Usage :
  python src/train.py              jeu de démonstration (data/demo_reviews.csv)
  python src/train.py --allocine   20 000 avis Allociné (téléchargés une fois)

Produit :
  models/sentiment.joblib   le pipeline entier (hors de Git, reconstructible)
  models/metrics.json       la mesure et son seuil (dans Git)
"""
import argparse
import json
import sys
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from donnees import GRAINE, PART_TEST, RACINE, charger, decouper  # noqa: E402

MODELE = RACINE / "models" / "sentiment.joblib"
METRIQUES = RACINE / "models" / "metrics.json"
SEUIL_F1 = 0.85


def construire() -> Pipeline:
    """Vectoriseur et modèle enfermés dans un seul objet."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Entraîne le classifieur de sentiment.")
    parser.add_argument("--allocine", action="store_true", help="entraîner sur le jeu Allociné")
    args = parser.parse_args()
    source = "allocine" if args.allocine else "demo"

    df = charger(source)
    print(f"Source : {source}, {len(df)} avis ({(df.label == 'negative').sum()} négatifs)")

    X_train, X_test, y_train, y_test = decouper(df)
    print(f"{len(X_train)} avis d'entraînement, {len(X_test)} de test")

    pipeline = construire()
    pipeline.fit(X_train, y_train)
    vocabulaire = len(pipeline.named_steps["tfidf"].vocabulary_)
    print(f"Vocabulaire : {vocabulaire} termes")

    y_pred = pipeline.predict(X_test)
    f1 = f1_score(y_test, y_pred, average="macro")
    accepte = f1 >= SEUIL_F1
    print(f"F1 macro sur le jeu de test : {f1:.3f} (seuil {SEUIL_F1}) -> {'ACCEPTÉ' if accepte else 'REFUSÉ'}")

    MODELE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODELE)
    metriques = {
        "source": source,
        "n_avis": int(len(df)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "part_test": PART_TEST,
        "random_state": GRAINE,
        "vocabulaire": vocabulaire,
        "f1_macro": round(float(f1), 4),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "rappel_negatif": round(float(recall_score(y_test, y_pred, pos_label="negative")), 4),
        "seuil_f1_macro": SEUIL_F1,
        "accepte": bool(accepte),
    }
    METRIQUES.write_text(json.dumps(metriques, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Modèle : {MODELE.relative_to(RACINE)} ; mesure : {METRIQUES.relative_to(RACINE)}")
    return 0 if accepte else 1


if __name__ == "__main__":
    sys.exit(main())
