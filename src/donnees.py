"""Chargement et découpage des données, partagés par train.py et evaluate.py.

Les deux scripts doivent voir exactement le même jeu de test : le découpage
vit donc ici, une seule fois, avec une graine fixe.
"""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

RACINE = Path(__file__).resolve().parents[1]
DEMO = RACINE / "data" / "demo_reviews.csv"
ALLOCINE_LOCAL = RACINE / "data" / "allocine.parquet"
ALLOCINE_URL = (
    "https://huggingface.co/datasets/tblard/allocine/resolve/main/"
    "allocine/validation-00000-of-00001.parquet"
)
GRAINE = 42
PART_TEST = 0.2


def charger(source: str) -> pd.DataFrame:
    """Renvoie un DataFrame à deux colonnes : review, label (positive/negative)."""
    if source == "demo":
        if not DEMO.exists():
            raise FileNotFoundError("data/demo_reviews.csv absent : lancez d'abord python src/make_demo.py")
        df = pd.read_csv(DEMO)
    elif source == "allocine":
        if not ALLOCINE_LOCAL.exists():
            print("Téléchargement du jeu Allociné (7,6 Mo), une seule fois...")
            pd.read_parquet(ALLOCINE_URL).to_parquet(ALLOCINE_LOCAL)
        df = pd.read_parquet(ALLOCINE_LOCAL)
        df["label"] = df["label"].map({0: "negative", 1: "positive"})
    else:
        raise ValueError(f"source inconnue : {source}")
    return df[["review", "label"]].dropna()


def decouper(df: pd.DataFrame):
    """Découpage stratifié 80/20, AVANT toute vectorisation (sinon fuite de données)."""
    return train_test_split(
        df["review"], df["label"], test_size=PART_TEST, random_state=GRAINE, stratify=df["label"]
    )
