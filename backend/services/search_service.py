"""
services/search_service.py

Détermine si un terme recherché correspond à un pays ou une ville,
pour rediriger l'utilisateur vers la bonne page (comme dans la maquette :
l'utilisateur tape "Japon" -> arrive directement sur la page Japon).
"""

from services.geo_service import rechercher_pays, rechercher_ville


def rechercher(terme: str) -> dict:
    """
    Retourne {"type": "pays", "nom": ...} ou
    {"type": "ville", "nom": ..., "pays": ...}, ou {"error": ...} si rien trouvé.
    """
    pays_trouve = rechercher_pays(terme)
    if pays_trouve:
        return {"type": "pays", "nom": pays_trouve}

    ville_trouvee = rechercher_ville(terme)
    if ville_trouvee:
        return {"type": "ville", "nom": ville_trouvee["nom"], "pays": ville_trouvee["pays"]}

    return {"error": f"Aucun résultat trouvé pour '{terme}'."}