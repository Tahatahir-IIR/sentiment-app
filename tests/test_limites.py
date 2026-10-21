"""Tests aux limites du contrat d'entrée (TP4, étape B).

PredictRequest promet un champ « text », chaîne de 1 à 2000 caractères.
Ce fichier vérifie cette promesse à ses frontières, puis au hasard (hypothesis).
"""
import json
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

ETIQUETTES_DU_CONTRAT = {"POSITIVE", "NEGATIVE", "INDETERMINE"}
# Tous les caractères que str.strip() retire : la règle de « vide » de predict() au TP2
BLANCS = [chr(c) for c in range(sys.maxunicode + 1) if chr(c).isspace()]


@pytest.fixture(scope="module")
def client():
    """Portée « module » : l'API démarre une fois pour tout le fichier (hypothesis l'exige)."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:  # le « with » exécute le lifespan : le modèle est chargé
        yield c


def en_json(valeur: object) -> bytes:
    """Corps de requête JSON, sous forme d'octets : permet aussi d'envoyer un corps invalide."""
    return json.dumps(valeur).encode("utf-8")


def assert_422_standard(reponse) -> None:
    """Un refus doit avoir la forme standard de FastAPI : une liste d'objets loc, msg, type."""
    assert reponse.status_code == 422
    detail = reponse.json()["detail"]
    assert isinstance(detail, list) and detail, f"detail n'est pas une liste d'erreurs : {detail!r}"
    for erreur in detail:
        assert {"loc", "msg", "type"} <= erreur.keys(), f"erreur sans loc, msg ou type : {erreur!r}"


CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="espaces-seuls"),
    # trouvé par hypothesis : U+0085 (NEL) est un blanc pour str.strip(), pas pour min_length
    pytest.param(en_json({"text": "\x85"}), 422, id="blanc-unicode-nel"),
    pytest.param(en_json({"text": "a"}), 200, id="un-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="autre-type"),
    pytest.param(b"pas du json", 422, id="pas-du-json"),
]


@pytest.mark.parametrize("corps, code_attendu", CAS)
def test_frontieres_du_contrat(client, corps, code_attendu):
    reponse = client.post("/predict", content=corps, headers={"Content-Type": "application/json"})
    assert reponse.status_code == code_attendu
    if code_attendu == 422:
        assert_422_standard(reponse)
    else:
        assert reponse.json()["label"] in ETIQUETTES_DU_CONTRAT


@settings(deadline=None)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda t: t.strip()))
def test_tout_texte_non_blanc_est_classe(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["label"] in ETIQUETTES_DU_CONTRAT
    assert 0.0 <= corps["score"] <= 1.0


@settings(deadline=None)
@given(texte=st.text(alphabet=st.sampled_from(BLANCS), min_size=1, max_size=50))
def test_tout_texte_blanc_est_refuse_par_le_schema(client, texte):
    assert_422_standard(client.post("/predict", json={"text": texte}))
