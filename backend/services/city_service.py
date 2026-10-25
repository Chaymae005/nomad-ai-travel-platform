"""
services/city_service.py

Assemble les données nécessaires pour peupler une page Ville, en combinant
RAG Wikivoyage (attractions, quartiers, présentation), météo, carte, et
suggestions culinaires générées par Gemini.
"""

import json
import unicodedata
from google.genai import types
from gemini.client import send_message
from agent.tools_external import obtenir_meteo_ville
from agent.rag import search_rag, resoudre_nom_pays_pour_rag
from services.maps_service import get_coordonnees_ville

def _resoudre_image_locale(nom: str) -> str:
    nfkd = unicodedata.normalize("NFKD", nom)
    cle = "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()
    cle = cle.replace(" ", "_").replace("'", "")
    return f"/images/{cle}.jpg"


INSTRUCTION_RESTAURANTS = (
    "Tu es un expert culinaire voyage. À partir du contexte fourni sur une "
    "ville/pays, suggère 4 spécialités culinaires ou types de restaurants "
    "à essayer. Base-toi UNIQUEMENT sur le contexte fourni pour la cuisine "
    "locale : n'invente JAMAIS de nom d'établissement réel (pas d'adresse, "
    "pas de nom de restaurant précis) puisque tu ne peux pas vérifier son "
    "existence — reste sur des types de plats ou catégories d'établissements.\n\n"
    "Réponds STRICTEMENT en JSON avec cette structure :\n"
    '{"suggestions": [{"nom": "ex: Ramen traditionnel", "description": "1 phrase"}]}'
)


def get_city_page_data(ville: str, pays: str) -> dict:
    """Assemble toutes les données nécessaires pour la page d'une ville."""

    coords = get_coordonnees_ville(ville)
    meteo = obtenir_meteo_ville(ville)

    nom_rag = resoudre_nom_pays_pour_rag(pays)

    presentation = attractions = quartiers = None
    if nom_rag:
        rag_presentation = search_rag(f"présentation de {ville}, {nom_rag}", category="general", country=nom_rag)
        rag_attractions = search_rag(f"attractions et lieux incontournables à {ville}", category="tourisme", country=nom_rag)
        rag_quartiers = search_rag(f"quartiers à visiter à {ville}", category="tourisme", country=nom_rag)

        presentation = rag_presentation.get("passages", [{}])[0].get("text") if "error" not in rag_presentation else None
        attractions = rag_attractions.get("passages", [{}])[0].get("text") if "error" not in rag_attractions else None
        quartiers = rag_quartiers.get("passages", [{}])[0].get("text") if "error" not in rag_quartiers else None

    return {
        "nom": ville,
        "pays": pays,
        "image_hero": _resoudre_image_locale(ville),
        "coordonnees": coords if "error" not in coords else None,
        "meteo": meteo if "error" not in meteo else None,
        "presentation": presentation,
        "attractions": attractions,
        "quartiers": quartiers,
        "source": "Wikivoyage RAG + Open-Meteo",
    }


def get_suggestions_restaurants(ville: str, pays: str) -> dict:
    """Génère des suggestions de spécialités/types de restaurants via Gemini + RAG."""

    nom_rag = resoudre_nom_pays_pour_rag(pays)
    if not nom_rag:
        return {"error": f"Aucune information disponible sur {pays} dans la base."}

    rag_cuisine = search_rag(f"cuisine et gastronomie de {nom_rag}", category="tourisme", country=nom_rag)
    if "error" in rag_cuisine:
        return {"error": "Pas assez d'informations culinaires disponibles."}

    contexte = "\n\n".join(p["text"] for p in rag_cuisine["passages"])

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Contexte sur la cuisine de {nom_rag} (ville : {ville}) :\n{contexte}")]
        )
    ]

    response = send_message(
        contents=contents,
        usage="agent",
        system_instruction=INSTRUCTION_RESTAURANTS,
        reponse_json=True,
    )

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, AttributeError):
        return {"error": "Impossible de générer les suggestions culinaires."}