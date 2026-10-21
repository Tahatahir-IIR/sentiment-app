"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
"""
import sys
from pathlib import Path
from typing import TypedDict

from api.schemas import Etiquette

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from predict import charger_modele  # noqa: E402  (fonctions du TP2, src/ ajouté juste au-dessus)
from predict import predict as _predict  # noqa: E402

# Sous ce seuil de confiance, l'API s'abstient : l'avis part vers un humain (TP4, étape C).
# 0,60 sur le jeu de test du TP2 : 72 % des avis traités, 2 erreurs au lieu de 7 (courbe_seuil.py).
SEUIL_ABSTENTION = 0.60

# Classes du modèle (TP2) vers étiquettes du contrat : explicite, pas un .upper() qui laisserait
# passer n'importe quelle chaîne. Toute autre classe fait refuser le démarrage.
CORRESPONDANCE: dict[str, Etiquette] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class Reponse(TypedDict):
    """Ce que l'API renvoie pour un avis : le contrat de PredictResponse."""

    label: Etiquette
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self) -> None:
        # échoue immédiatement si le joblib manque : on ne démarre pas sans modèle
        pipeline = charger_modele()
        inconnues = sorted({str(c) for c in pipeline.classes_} - CORRESPONDANCE.keys())
        if inconnues:
            raise ValueError(f"classes inattendues dans le modèle : {inconnues}")

    def predict(self, text: str) -> Reponse:
        """Renvoie l'étiquette du contrat, la confiance et un aperçu du texte."""
        r = _predict(text)
        label: Etiquette = CORRESPONDANCE[r["label"]] if r["score"] >= SEUIL_ABSTENTION else "INDETERMINE"
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans src/predict.py)."""
    return SentimentClassifier()
