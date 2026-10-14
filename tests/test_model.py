"""Tests du modèle (TP2).

Deux tests lisent models/metrics.json, versionné : ils tournent partout, CI comprise.
Deux tests appellent predict() : ils sont ignorés si le modèle n'est pas là,
ce qui est le cas en intégration continue (le modèle n'est jamais commité).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
METRIQUES = ROOT / "models" / "metrics.json"
MODELE = ROOT / "models" / "sentiment.joblib"
CLES = {"source", "n_train", "n_test", "f1_macro", "seuil_f1_macro"}

besoin_modele = pytest.mark.skipif(not MODELE.exists(), reason="modèle absent : python src/train.py")


@pytest.fixture(scope="module")
def metriques() -> dict:
    assert METRIQUES.exists(), "models/metrics.json absent : lancez python src/train.py puis commitez-le"
    return json.loads(METRIQUES.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def predict():
    sys.path.insert(0, str(ROOT / "src"))
    from predict import predict as fonction
    return fonction


def test_metrics_file_is_complete(metriques):
    manquantes = CLES - metriques.keys()
    assert not manquantes, f"clés absentes de metrics.json : {sorted(manquantes)}"
    assert metriques["n_test"] > 0


def test_f1_above_threshold(metriques):
    assert metriques["f1_macro"] >= metriques["seuil_f1_macro"], (
        f"F1 macro {metriques['f1_macro']} sous le seuil {metriques['seuil_f1_macro']}"
    )


@besoin_modele
def test_predict_returns_label_and_score(predict):
    r = predict("Livraison rapide, produit conforme, je recommande.")
    assert r["label"] in {"positive", "negative"}
    assert 0.5 <= r["score"] <= 1.0


@besoin_modele
def test_predict_obvious_negative(predict):
    r = predict("Produit cassé, service client injoignable, très déçu, à éviter absolument.")
    assert r["label"] == "negative"
