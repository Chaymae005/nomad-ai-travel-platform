"""
services/country_service.py

Assemble les données nécessaires pour peupler une page Pays, en combinant
plusieurs sources : API pays, RAG qualitatif, météo/fuseau horaire, image.
Contrairement à agent/tools_external.py (pensé pour Gemini via function
calling), ce service est appelé directement par les routes FastAPI.
"""

import json
from google.genai import types
from gemini.client import send_message
from agent.tools_external import get_country_info, rechercher_image, obtenir_meteo_ville
from agent.rag import search_rag, resoudre_nom_pays_pour_rag
from services.traductions import normaliser_nom_pays
from services.city_service import _resoudre_image_locale
from pathlib import Path

# Liste statique de villes populaires par pays (les pays déjà indexés dans le RAG)
VILLES_POPULAIRES = {
    "Japon": ["Tokyo", "Kyoto", "Osaka"],
    "Italie": ["Rome", "Venise", "Florence"],
    "France": ["Paris", "Nice", "Lyon"],
    "Maroc": ["Marrakech", "Casablanca", "Fès"],
    "Espagne": ["Barcelone", "Madrid", "Séville"],
    "Grèce": ["Athènes", "Santorin", "Mykonos"],
    "Thaïlande": ["Bangkok", "Phuket", "Chiang Mai"],
    "Égypte": ["Le Caire", "Louxor", "Alexandrie"],
    "Turquie": ["Istanbul", "Antalya", "Cappadoce"],
    "Inde": ["Delhi", "Mumbai", "Jaipur"],
    "Chine": ["Pékin", "Shanghai", "Xi'an"],
    "Indonésie": ["Bali", "Jakarta", "Yogyakarta"],
    "Brésil": ["Rio de Janeiro", "São Paulo", "Salvador"],
    "Australie": ["Sydney", "Melbourne", "Cairns"],
    "États-Unis": ["New York", "Los Angeles", "San Francisco"],
    "Russie": ["Moscou", "Saint-Pétersbourg", "Kazan"],
    "Royaume-Uni": ["Londres", "Édimbourg", "Manchester"],
    "Tunisie": ["Tunis", "Sousse", "Djerba"],
    "Kenya": ["Nairobi", "Mombasa", "Nakuru"],
    "Tanzanie": ["Dar es Salaam", "Zanzibar", "Arusha"],
    "Chili": ["Santiago", "Valparaíso", "San Pedro de Atacama"],
    "Colombie": ["Bogotá", "Carthagène", "Medellín"],
    "Argentine": ["Buenos Aires", "Bariloche", "Mendoza"],
    "Nouvelle-Zélande": ["Auckland", "Queenstown", "Wellington"],
    "Fidji": ["Nadi", "Suva", "Denarau"],
}

INSTRUCTION_SAISONS = (
    "Tu es un expert voyage. À partir du contexte fourni sur un pays, "
    "évalue chacune des 4 saisons (printemps, été, automne, hiver) pour "
    "y voyager. Base-toi UNIQUEMENT sur les informations du contexte : "
    "n'invente aucun détail climatique ou d'affluence qui n'y figure pas. "
    "Si le contexte ne mentionne rien sur une saison précise, donne une "
    "évaluation prudente et généraliste plutôt que d'inventer.\n\n"
    "Réponds STRICTEMENT en JSON, avec cette structure exacte :\n"
    "{\n"
    '  "printemps": {"recommandation": "ideal|bon|moyen|deconseille", "justification": "..."},\n'
    '  "ete": {"recommandation": "...", "justification": "..."},\n'
    '  "automne": {"recommandation": "...", "justification": "..."},\n'
    '  "hiver": {"recommandation": "...", "justification": "..."}\n'
    "}\n"
    "Chaque justification doit être concise (1-2 phrases max)."
)


PRESENTATIONS_PATH = Path("data/curated/presentations.json")


def _charger_presentations() -> dict:
    if not PRESENTATIONS_PATH.exists():
        return {}
    try:
        with open(PRESENTATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def obtenir_presentation_pays(country_name: str, nom_rag: str | None, info: dict) -> str:
    """
    Retourne une présentation unifiée, chaleureuse et concise du pays.
    1. Lit en priorité dans data/curated/presentations.json.
    2. Si absent, génère à la volée avec Gemini et sauvegarde dans le fichier.
    3. Fallback élégant basé sur les données pays si indisponible.
    """
    presentations = _charger_presentations()

    for cle in [nom_rag or "", country_name, info.get("name", "")]:
        if cle and cle in presentations:
            return presentations[cle]
        if cle:
            for k, v in presentations.items():
                if k.lower() == cle.lower():
                    return v

    nom_affiche = nom_rag or country_name
    try:
        from gemini.client import send_message
        prompt = (
            f"Tu es un guide voyage passionné et bienveillant. Rédige une présentation courte, vivante et amicale pour la page destination d'un pays : {nom_affiche}.\n"
            "Contraintes :\n"
            "- 1 à 2 courts paragraphes (environ 100 à 130 mots au total).\n"
            "- Mentionne naturellement sa situation géographique (où il se trouve, bordé par quoi, pays voisins).\n"
            "- Mentionne son nom local et comment les habitants l'appellent ou le prononcent.\n"
            "- Mentionne sa monnaie.\n"
            "- Évoque son histoire et son ambiance culturelle/mode de vie de manière chaleureuse.\n"
            "- Rédige dans un style fluide, amical et invitant au voyage, sans puces ni titres techniques."
        )
        res = send_message(prompt, usage="agent")
        texte = res.text.strip()
        if texte:
            presentations[nom_affiche] = texte
            try:
                with open(PRESENTATIONS_PATH, "w", encoding="utf-8") as f:
                    json.dump(presentations, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return texte
    except Exception:
        pass

    region = info.get("region", "le monde")
    capitale = info.get("capital", "")
    devises = ", ".join(info.get("devises", [])) or "la monnaie locale"
    return (
        f"Bienvenue en {nom_affiche} ! Situé en {region}, ce magnifique pays séduit par la richesse de ses paysages "
        f"et la générosité de ses habitants. De sa capitale {capitale} à ses provinces pittoresques, vous découvrirez "
        f"une histoire captivante et une douceur de vivre incomparable. Préparez vos {devises} et laissez-vous transporter "
        f"par des rencontres chaleureuses et des découvertes inoubliables."
    )


def get_country_page_data(country_name: str) -> dict:
    """Assemble toutes les données nécessaires pour la page d'un pays."""

    country_name = normaliser_nom_pays(country_name)

    info = get_country_info(country_name)
    if "error" in info:
        return {"error": info["error"]}

    # Résolution fiable du nom RAG (par code ISO), une seule fois
    nom_rag = resoudre_nom_pays_pour_rag(country_name)

    presentation = obtenir_presentation_pays(country_name, nom_rag, info)

    # Fuseau horaire déduit via la météo de la capitale
    fuseau_horaire = None
    if info.get("capital") and info["capital"] != "Inconnu":
        meteo_capitale = obtenir_meteo_ville(info["capital"])
        if "error" not in meteo_capitale:
            fuseau_horaire = meteo_capitale.get("timezone")

    return {
        "nom": info.get("name"),
        "capitale": info.get("capital"),
        "langues": info.get("languages"),
        "devises": info.get("currencies"),
        "fuseau_horaire": fuseau_horaire,
        "population": info.get("population"),
        "region": info.get("region"),
        "drapeau_url": info.get("flag_url"),
        "image_hero": _resoudre_image_locale(nom_rag or country_name),
        "presentation": presentation,
        "villes_populaires": VILLES_POPULAIRES.get(nom_rag, []) if nom_rag else [],
        "source": "countries.dev + Wikivoyage",
    }


SAISONS_PATH = Path("data/curated/saisons.json")


def _charger_saisons() -> dict:
    if not SAISONS_PATH.exists():
        return {}
    with open(SAISONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_meilleure_periode(country_name: str) -> dict:
    """Lit la recommandation par saison pré-générée par pipeline/generer_saisons.py."""

    country_name = normaliser_nom_pays(country_name)
    nom_rag = resoudre_nom_pays_pour_rag(country_name)
    if not nom_rag:
        return {"error": f"Aucune information disponible sur {country_name} dans la base."}

    saisons = _charger_saisons()
    resultat = saisons.get(nom_rag)
    if not resultat:
        return {"error": f"Aucune évaluation saisonnière disponible pour {country_name}."}

    return resultat