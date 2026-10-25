"""
services/recommendation_service.py

Système de recommandation de destinations par similarité de contenu
(content-based filtering), basé sur les embeddings déjà générés pour
le RAG Wikivoyage (ChromaDB). Le "profil" d'un utilisateur est le
centroïde des vecteurs de ses pays favoris ; on recommande les pays
dont les vecteurs sont les plus proches de ce centroïde.
"""

import numpy as np
from agent.rag import _collection, resoudre_nom_pays_pour_rag


def _embedding_moyen_pays(noms_rag: list[str]) -> np.ndarray | None:
    """Récupère tous les chunks des pays donnés et retourne leur vecteur moyen."""
    resultats = _collection.get(
        where={"country": {"$in": noms_rag}},
        include=["embeddings"],
    )
    embeddings = resultats.get("embeddings")
    if embeddings is None or len(embeddings) == 0:
        return None
    return np.mean(embeddings, axis=0)


def recommander_destinations(favoris_pays: list[str], n_recommandations: int = 3) -> list[dict]:
    """
    favoris_pays : noms de pays tels que stockés dans les favoris de
    l'utilisateur (n'importe quelle langue/graphie reconnue par pycountry).
    Retourne une liste de {"pays": nom_fr, "score_similarite": float},
    triée par pertinence, en excluant les pays déjà en favoris.
    """
    noms_rag = [resoudre_nom_pays_pour_rag(p) for p in favoris_pays]
    noms_rag = [n for n in noms_rag if n]  # on ignore les favoris hors RAG

    if not noms_rag:
        return []

    vecteur_profil = _embedding_moyen_pays(noms_rag)
    if vecteur_profil is None:
        return []

    resultats = _collection.query(
        query_embeddings=[vecteur_profil.tolist()],
        n_results=50,  # large, pour avoir assez de matière après dédoublonnage/filtrage
        include=["metadatas", "distances"],
    )

    metadatas = resultats.get("metadatas", [[]])[0]
    distances = resultats.get("distances", [[]])[0]

    meilleurs_par_pays = {}
    for meta, dist in zip(metadatas, distances):
        pays = meta.get("country")
        if not pays or pays in noms_rag:
            continue  # on exclut les pays déjà en favoris
        # on garde la meilleure distance (la plus faible) rencontrée pour ce pays
        if pays not in meilleurs_par_pays or dist < meilleurs_par_pays[pays]:
            meilleurs_par_pays[pays] = dist

    classement = sorted(meilleurs_par_pays.items(), key=lambda x: x[1])[:n_recommandations]

    return [
        {"pays": pays, "score_similarite": round(1 - dist, 3)}
        for pays, dist in classement
    ]