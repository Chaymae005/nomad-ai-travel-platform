"""
Descriptions des tools transmises à Gemini (function calling).
Ce fichier ne contient AUCUNE logique d'exécution réelle — juste le
"schéma" que le modèle utilise pour savoir quels outils existent et
comment les appeler. Le code réel est dans agent/tools_external.py.
"""

from google.genai import types

get_weather_declaration = types.FunctionDeclaration(
    name="get_weather",
    description=(
        "Retourne la météo actuelle et les prévisions pour une ville donnée, "
        "en utilisant ses coordonnées géographiques (latitude/longitude)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Latitude de la ville, ex: 48.8566 pour Paris"
            },
            "longitude": {
                "type": "number",
                "description": "Longitude de la ville, ex: 2.3522 pour Paris"
            },
            "city_name": {
                "type": "string",
                "description": "Nom de la ville, utilisé uniquement pour la lisibilité de la réponse"
            }
        },
        "required": ["latitude", "longitude"]
    }
)


get_country_info_declaration = types.FunctionDeclaration(
    name="get_country_info",
    description=(
        "Retourne des informations structurées et fiables sur un pays : "
        "capitale, région, population, superficie, langues officielles, "
        "monnaies, drapeau. À utiliser pour toute question factuelle "
        "précise sur un pays plutôt que de deviner."
    ),
    parameters={
        "type": "object",
        "properties": {
            "country_name": {
                "type": "string",
                "description": "Nom du pays en anglais de préférence, ex: 'France', 'Morocco', 'Japan'"
            }
        },
        "required": ["country_name"]
    }
)


search_rag_declaration = types.FunctionDeclaration(
    name="search_rag",
    description=(
        "Recherche des informations qualitatives et descriptives sur un pays "
        "dans une base de connaissances (Wikivoyage) : culture, ambiance, "
        "quoi visiter, meilleure saison pour voyager, coutumes, conseils de "
        "sécurité, santé, histoire. À utiliser pour toute question ouverte "
        "ou descriptive sur un pays, PAS pour des données chiffrées précises "
        "(pour ça, utilise get_country_info) ni pour la météo en temps réel "
        "(pour ça, utilise get_weather)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "La question ou le sujet recherché, reformulé clairement, "
                    "ex: 'meilleure saison pour visiter la Thaïlande', "
                    "'que voir au Maroc', 'sécurité en Égypte'"
                )
            },
            "category": {
                "type": "string",
                "enum": ["tourisme", "histoire", "general"],
                "description": (
                    "Catégorie du contenu recherché, si elle est déterminable "
                    "à partir de la question : 'tourisme' (climat, villes, "
                    "sécurité, santé, coutumes), 'histoire', ou 'general' "
                    "(géographie, présentation générale du pays). Si la "
                    "catégorie n'est pas claire, ne pas inclure ce paramètre "
                    "pour rechercher dans toutes les catégories."
                )
            }
        },
        "required": ["query"]
    }
)




get_wikipedia_summary_declaration = types.FunctionDeclaration(
    name="get_wikipedia_summary",
    description=(
        "Retourne un résumé encyclopédique fiable sur N'IMPORTE QUEL sujet "
        "(personne, lieu, concept, équipe sportive, terme technique, notion "
        "de santé, d'économie, d'immobilier, etc.), via Wikipedia. À utiliser "
        "chaque fois qu'une question porte sur une définition, une "
        "explication générale, ou des informations factuelles sur un sujet "
        "qui n'est pas couvert par un outil plus spécifique."
    ),
    parameters={
        "type": "object",
        "properties": {
            "sujet": {
                "type": "string",
                "description": "Le sujet recherché, ex: 'Real Madrid', 'diabète', 'blockchain', 'prêt hypothécaire'"
            },
            "langue": {
                "type": "string",
                "enum": ["fr", "en"],
                "description": "Langue de la recherche Wikipedia, 'fr' par défaut sauf si le sujet est mieux documenté en anglais"
            }
        },
        "required": ["sujet"]
    }
)





AVAILABLE_TOOLS = [
    types.Tool(function_declarations=[
        get_weather_declaration,
        get_country_info_declaration,
        search_rag_declaration,
        get_wikipedia_summary_declaration,
      
        
    ])
]