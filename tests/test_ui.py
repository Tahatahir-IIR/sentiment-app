"""Tests de l'interface (TP3).

Ils importent ui/helpers.py sans lancer Streamlit et sans le modèle :
un faux prédicteur suffit, donc ils tournent aussi en intégration continue.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ui"))
import helpers  # noqa: E402


def faux_predicteur(texte):
    """Négatif si le texte contient « cassé », confiance faible si « mais »."""
    label = "negative" if "cassé" in texte else "positive"
    score = 0.55 if "mais" in texte else 0.95
    return {"label": label, "score": score}


def test_classer_ajoute_un_verdict():
    net = helpers.classer("Produit cassé", faux_predicteur)
    assert net["verdict"] == "negative" and net["incertain"] is False
    hesitant = helpers.classer("Bien mais cassé", faux_predicteur)
    assert hesitant["verdict"] == "à vérifier" and hesitant["incertain"] is True
    with pytest.raises(ValueError):
        helpers.classer("   ", faux_predicteur)


def test_predire_lot_ecarte_les_lignes_vides():
    df = pd.DataFrame(
        {"review": ["Produit cassé", "", None, "Très bien", "Bien mais cassé"]}
    )
    sortie = helpers.predire_lot(df, faux_predicteur)
    assert len(sortie) == 3
    assert list(sortie["verdict"]) == ["negative", "positive", "à vérifier"]
    with pytest.raises(KeyError):
        helpers.predire_lot(pd.DataFrame({"texte": ["x"]}), faux_predicteur)


def test_resumer_compte_les_negatifs_et_les_cas_a_verifier():
    df = helpers.predire_lot(
        pd.DataFrame({"review": ["Produit cassé", "Très bien", "Bien mais cassé"]}),
        faux_predicteur,
    )
    r = helpers.resumer(df)
    assert r["total"] == 3
    assert r["negatifs"] == 2
    assert r["part_negatifs"] == 66.7
    assert r["a_verifier"] == 1
