# services/traveler_service.py

"""
services/traveler_service.py

Lit les tags voyageurs pré-générés par pipeline/generer_tags_voyageurs.py.
Aucun appel Gemini ici -- juste la lecture d'un résultat déjà calculé.
"""

import json
from pathlib import Path

TAGS_PATH = Path("data/curated/tags_voyageurs.json")

PROFILS_VALIDES = {"famille", "couple", "amis", "solo"}


def _charger_tags() -> dict:
    if not TAGS_PATH.exists():
        return {}
    with open(TAGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_destinations_par_profil(profil: str, n: int = 5) -> list[dict]:
    """
    Retourne les pays les mieux notés pour un profil donné
    (famille, couple, amis, solo), triés par pertinence.
    """
    if profil not in PROFILS_VALIDES:
        return []

    ordre_recommandation = {"ideal": 3, "bon": 2, "moyen": 1, "deconseille": 0}
    tags = _charger_tags()

    resultats = []
    for pays, jugements in tags.items():
        jugement = jugements.get(profil)
        if not jugement:
            continue
        resultats.append({
            "pays": pays,
            "recommandation": jugement["recommandation"],
            "justification": jugement["justification"],
            "_score": ordre_recommandation.get(jugement["recommandation"], 0),
        })

    resultats.sort(key=lambda x: x["_score"], reverse=True)
    for r in resultats:
        del r["_score"]

    return resultats[:n]