"""Logique de l'interface, séparée de l'affichage.

Les tests importent ce module sans lancer Streamlit : rien ici ne dépend de st.
L'interface n'invente aucune logique de prédiction, elle appelle predict() du TP2.
"""
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
SEUIL_INCERTITUDE = 0.60   # en dessous, on affiche « à vérifier »


def charger_predicteur():
    """Renvoie la fonction predict() du TP2, ou une erreur qui dit quoi faire."""
    if not MODELE.exists():
        raise FileNotFoundError(
            "models/sentiment.joblib absent : lancez d'abord python src/train.py")
    sys.path.insert(0, str(RACINE / "src"))
    from predict import predict
    return predict


def classer(texte, predicteur):
    """Ajoute à la prédiction brute un verdict lisible par un non-spécialiste."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    resultat = dict(predicteur(texte))
    incertain = resultat["score"] < SEUIL_INCERTITUDE
    resultat["verdict"] = "à vérifier" if incertain else resultat["label"]
    resultat["incertain"] = incertain
    return resultat


def predire_lot(df: pd.DataFrame, predicteur, colonne="review") -> pd.DataFrame:
    """Classe chaque ligne non vide d'un fichier ; refuse un fichier sans la bonne colonne."""
    if colonne not in df.columns:
        raise KeyError(f"colonne '{colonne}' absente du fichier")
    lignes = [classer(str(t), predicteur) for t in df[colonne].fillna("") if str(t).strip()]
    if not lignes:
        raise ValueError("aucun avis exploitable dans le fichier")
    sortie = df.loc[df[colonne].fillna("").astype(str).str.strip() != ""].copy()
    sortie["prediction"] = [l["label"] for l in lignes]
    sortie["confiance"] = [round(l["score"], 3) for l in lignes]
    sortie["verdict"] = [l["verdict"] for l in lignes]
    return sortie


def resumer(df: pd.DataFrame) -> dict:
    """La métrique produit : ce que l'équipe relation client regarde."""
    negatifs = int((df["prediction"] == "negative").sum())
    a_verifier = int((df["verdict"] == "à vérifier").sum())
    return {
        "total": len(df),
        "negatifs": negatifs,
        "part_negatifs": round(100 * negatifs / len(df), 1) if len(df) else 0.0,
        "a_verifier": a_verifier,
        "confiance_moyenne": round(float(df["confiance"].mean()), 3) if len(df) else 0.0,
    }
