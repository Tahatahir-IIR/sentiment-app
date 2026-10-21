"""Interface de démonstration du classifieur de sentiment (TP3).

Usage, à la racine du dépôt : streamlit run ui/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers import (
    SEUIL_INCERTITUDE,
    charger_predicteur,
    classer,
    predire_lot,
    resumer,
)  # noqa: E402

st.set_page_config(page_title="Avis clients : tri par sentiment", page_icon="💬")
st.title("Avis clients : faire remonter les négatifs")
st.caption(
    "Modèle du TP2 (TF-IDF et régression logistique). "
    f"Sous {SEUIL_INCERTITUDE:.0%} de confiance, l'avis est envoyé à un agent."
)


@st.cache_resource
def predicteur():
    """Chargé une seule fois : sans cache, le modèle serait relu à chaque clic."""
    return charger_predicteur()


try:
    predire = predicteur()
except FileNotFoundError as erreur:
    st.error(str(erreur))
    st.info("Dans un terminal, à la racine du dépôt : `python src/train.py --allocine`")
    st.stop()

onglet_avis, onglet_lot, onglet_aide = st.tabs(
    ["Un avis", "Un fichier CSV", "Comment ça marche"]
)

with onglet_avis:
    texte = st.text_area(
        "Avis client",
        height=120,
        placeholder="Produit cassé à l'arrivée et service client injoignable.",
    )
    if st.button("Analyser", type="primary"):
        try:
            r = classer(texte, predire)
        except ValueError:
            st.warning("Saisissez un avis avant d'analyser.")
        else:
            if r["incertain"]:
                st.warning(f"À vérifier par un agent (penche vers « {r['label']} »)")
            elif r["label"] == "negative":
                st.error("Avis négatif : à traiter en priorité")
            else:
                st.success("Avis positif")
            st.progress(float(r["score"]), text=f"Confiance : {r['score']:.0%}")

with onglet_lot:
    fichier = st.file_uploader("Fichier CSV avec une colonne « review »", type="csv")
    if fichier is not None:
        try:
            df = predire_lot(pd.read_csv(fichier), predire)
        except (KeyError, ValueError) as erreur:
            st.error(str(erreur).strip("'\""))
        else:
            r = resumer(df)
            c1, c2, c3 = st.columns(3)
            c1.metric("Avis analysés", r["total"])
            c2.metric(
                "Avis négatifs détectés", f"{r['negatifs']} ({r['part_negatifs']} %)"
            )
            c3.metric("Cas à vérifier", r["a_verifier"])
            st.bar_chart(df["verdict"].value_counts())
            df = df.sort_values(["prediction", "confiance"], ascending=[True, False])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Télécharger les résultats",
                df.to_csv(index=False).encode("utf-8"),
                file_name="avis_classes.csv",
                mime="text/csv",
            )

with onglet_aide:
    st.markdown(
        f"""
**Ce que fait l'outil.** Il lit un avis et prédit s'il est positif ou négatif,
avec une confiance entre 50 % et 100 %.

**Les trois verdicts.**
- Rouge : avis négatif, à traiter en priorité.
- Vert : avis positif.
- Orange : confiance sous {SEUIL_INCERTITUDE:.0%}, un agent doit le lire.

**Ses limites.** Le modèle compte les mots sans regarder leur ordre. Un avis qui
commence bien et finit mal (« livraison rapide, mais produit cassé ») le trompe
souvent : c'est pour ces cas que le verdict orange existe.

**D'où il vient.** Entraîné sur 16 000 avis Allociné, F1 macro 0,920 sur 4 000 avis de test.
"""
    )
