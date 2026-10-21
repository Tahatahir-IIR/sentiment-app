"""Génère le jeu de démonstration : 290 avis clients, 145 de chaque classe.

Composition :
  - 80 avis nettement positifs
  - 80 avis nettement négatifs
  - 100 avis mitigés : une moitié d'un sentiment, un retournement, une moitié
    de l'autre. L'étiquette suit la seconde moitié, celle qui conclut.
  - 30 avis neutres, factuels, avec une légère pente qui fixe l'étiquette.

Usage : python src/make_demo.py
Produit : data/demo_reviews.csv (régénérable, donc hors de Git)
"""

import random
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "data" / "demo_reviews.csv"
GRAINE = 42

POSITIF = [
    "livraison rapide et colis bien protégé",
    "produit conforme à la description",
    "service client réactif et aimable",
    "très bon rapport qualité prix",
    "qualité impeccable, je suis ravi",
    "installation simple et notice claire",
    "le vendeur a répondu en moins d'une heure",
    "article solide et bien fini",
    "remboursement effectué sans discussion",
    "taille parfaite, tissu agréable",
    "batterie qui tient toute la journée",
    "emballage soigné, cadeau parfait",
]
NEGATIF = [
    "colis arrivé abîmé et incomplet",
    "produit cassé à l'arrivée",
    "service client injoignable",
    "commande jamais reçue",
    "remboursement toujours en attente",
    "qualité médiocre, déçu",
    "notice illisible et pièces manquantes",
    "l'application plante sans arrêt",
    "article différent de la photo",
    "livraison avec trois semaines de retard",
    "le tissu s'est déchiré au premier lavage",
    "batterie morte au bout d'une heure",
]
CONCLUSION_POS = [
    "je recommande",
    "je rachèterai",
    "très satisfait",
    "cinq étoiles mérité",
]
CONCLUSION_NEG = [
    "je ne recommande pas",
    "à éviter",
    "très déçu",
    "plus jamais chez eux",
]
RETOURNEMENT = [
    "mais finalement",
    "sauf que ensuite",
    "pourtant au bout du compte",
    "mais au final",
]
NEUTRE = [
    "commande passée lundi, reçue jeudi",
    "article reçu dans le carton d'origine",
    "le produit correspond à la référence commandée",
    "livré par le transporteur habituel",
    "utilisé deux fois pour l'instant",
]
PENTE_POS = ["rien à redire", "ça fait le travail"]
PENTE_NEG = ["rien d'extraordinaire", "un peu cher pour ce que c'est"]


def phrase(rng, fragments, n):
    return ", ".join(rng.sample(fragments, n))


def net(rng, fragments, conclusions):
    texte = phrase(rng, fragments, rng.choice([2, 3]))
    return f"{texte[0].upper()}{texte[1:]}, {rng.choice(conclusions)}."


def mitige(rng, debut, fin):
    """Pas de conclusion explicite : seul l'ordre des deux moitiés porte l'étiquette."""
    texte = f"{phrase(rng, debut, rng.choice([1, 2]))}, {rng.choice(RETOURNEMENT)} {phrase(rng, fin, 2)}."
    return texte[0].upper() + texte[1:]


def neutre(rng, pente):
    texte = f"{phrase(rng, NEUTRE, 2)}, {rng.choice(pente)}."
    return texte[0].upper() + texte[1:]


def generer() -> pd.DataFrame:
    rng = random.Random(GRAINE)
    lignes = []
    lignes += [
        (net(rng, POSITIF, CONCLUSION_POS), "positive", "net") for _ in range(80)
    ]
    lignes += [
        (net(rng, NEGATIF, CONCLUSION_NEG), "negative", "net") for _ in range(80)
    ]
    lignes += [(mitige(rng, NEGATIF, POSITIF), "positive", "mitigé") for _ in range(50)]
    lignes += [(mitige(rng, POSITIF, NEGATIF), "negative", "mitigé") for _ in range(50)]
    lignes += [(neutre(rng, PENTE_POS), "positive", "neutre") for _ in range(15)]
    lignes += [(neutre(rng, PENTE_NEG), "negative", "neutre") for _ in range(15)]
    rng.shuffle(lignes)
    return pd.DataFrame(lignes, columns=["review", "label", "type"])


if __name__ == "__main__":
    df = generer()
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SORTIE, index=False)
    print(f"{len(df)} avis écrits dans {SORTIE.relative_to(RACINE)}")
    print(df["label"].value_counts().to_string())
    print(df["type"].value_counts().to_string())
