"""Prédiction sur un texte : la seule fonction que l'interface et l'API appelleront.

Usage : python src/predict.py "Produit cassé à l'arrivée"
"""
import sys
from functools import lru_cache
from pathlib import Path

import joblib

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"


@lru_cache(maxsize=1)
def _pipeline():
    if not MODELE.exists():
        raise FileNotFoundError("models/sentiment.joblib absent : lancez d'abord python src/train.py")
    return joblib.load(MODELE)


def predict(texte: str) -> dict:
    """Renvoie {"label": "positive" ou "negative", "score": confiance entre 0,5 et 1}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = _pipeline()
    probas = pipeline.predict_proba([texte])[0]
    i = int(probas.argmax())
    return {"label": str(pipeline.classes_[i]), "score": float(probas[i])}


if __name__ == "__main__":
    for texte in sys.argv[1:] or ["Livraison rapide, produit conforme, je recommande."]:
        r = predict(texte)
        print(f"{r['label']:9s} {r['score']:.3f}  <- {texte}")
