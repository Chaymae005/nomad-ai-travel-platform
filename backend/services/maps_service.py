"""
services/maps_service.py

Calcul de distance et durée de trajet entre deux villes, et géocodage
pour affichage sur une carte interactive. Utilise geo_service (geonamescache)
pour la résolution des villes, et OpenRouteService pour le calcul d'itinéraire
routier réel (distance + durée).
"""

import os
import requests
from services.geo_service import rechercher_ville

ORS_DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


def _geocoder_ville(nom_ville: str) -> dict | None:
    """Retourne {latitude, longitude, nom} pour une ville, ou None si introuvable."""
    ville = rechercher_ville(nom_ville)
    if ville is None:
        return None
    return {"latitude": ville["latitude"], "longitude": ville["longitude"], "nom": ville["nom"]}


def get_coordonnees_ville(nom_ville: str) -> dict:
    """Pour afficher un marqueur sur la carte interactive."""
    coords = _geocoder_ville(nom_ville)
    if coords is None:
        return {"error": f"Ville introuvable : '{nom_ville}'"}
    return {**coords, "source": "geonamescache"}


def calculer_distance_trajet(ville_depart: str, ville_arrivee: str) -> dict:
    """
    Calcule la distance routière et la durée estimée du trajet en voiture
    entre deux villes, via OpenRouteService.
    """
    depart = _geocoder_ville(ville_depart)
    arrivee = _geocoder_ville(ville_arrivee)

    if depart is None:
        return {"error": f"Ville de départ introuvable : '{ville_depart}'"}
    if arrivee is None:
        return {"error": f"Ville d'arrivée introuvable : '{ville_arrivee}'"}

    cle = os.getenv("OPENROUTESERVICE_API_KEY")
    if not cle:
        return {"error": "Clé OpenRouteService non configurée."}

    try:
        response = requests.get(
            ORS_DIRECTIONS_URL,
            params={
                "api_key": cle,
                "start": f"{depart['longitude']},{depart['latitude']}",
                "end": f"{arrivee['longitude']},{arrivee['latitude']}",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Impossible de calculer le trajet : {e}"}

    data = response.json()
    features = data.get("features")
    if not features:
        return {"error": "Aucun itinéraire trouvé entre ces deux villes (trajet routier impossible, ex: séparées par un océan)."}

    summary = features[0]["properties"]["summary"]
    distance_km = round(summary["distance"] / 1000, 1)
    duree_heures = round(summary["duration"] / 3600, 1)

    return {
        "ville_depart": depart["nom"],
        "ville_arrivee": arrivee["nom"],
        "distance_km": distance_km,
        "duree_estimee_heures": duree_heures,
        "coordonnees_depart": {"latitude": depart["latitude"], "longitude": depart["longitude"]},
        "coordonnees_arrivee": {"latitude": arrivee["latitude"], "longitude": arrivee["longitude"]},
        "source": "OpenRouteService",
    }