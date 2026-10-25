# services/season_service.py

"""
services/season_service.py

Lit les évaluations saisonnières pré-générées par pipeline/generer_saisons.py
et retourne, pour une saison donnée, les destinations les mieux notées --
symétrique à traveler_service.py mais par saison plutôt que par profil.
"""

import json
from pathlib import Path

SAISONS_PATH = Path("data/curated/saisons.json")

SAISONS_VALIDES = {"printemps", "ete", "automne", "hiver"}


def _charger_saisons() -> dict:
    if not SAISONS_PATH.exists():
        return {}
    with open(SAISONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_destinations_par_saison(saison: str, n: int = 5) -> list[dict]:
    """
    Retourne les pays les mieux notés pour une saison donnée
    (printemps, ete, automne, hiver), triés par pertinence.
    """
    if saison not in SAISONS_VALIDES:
        return []

    ordre_recommandation = {"ideal": 3, "bon": 2, "moyen": 1, "deconseille": 0}
    tous_les_pays = _charger_saisons()

    resultats = []
    for pays, jugements in tous_les_pays.items():
        jugement = jugements.get(saison)
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