"""
Couche bas niveau : initialise le client Gemini et expose une fonction
générique pour envoyer une requête (avec ou sans tools).
Aucune logique métier ici — ça, c'est le rôle de agent/orchestrator.py.
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

load_dotenv()

MODEL_NAME = "gemini-flash-latest"

# Chaque usage peut avoir PLUSIEURS clés, séparées par des virgules dans .env
VARIABLES_PAR_USAGE = {
    "agent": "GEMINI_API_KEY_AGENT",
    "saisons": "GEMINI_API_KEY_SAISONS",
    "voyageurs": "GEMINI_API_KEY_VOYAGEURS",
}


def _obtenir_cles(usage: str) -> list[str]:
    variable = VARIABLES_PAR_USAGE.get(usage)
    if variable is None:
        raise ValueError(f"Usage inconnu : '{usage}'.")

    valeur = os.getenv(variable)
    if not valeur:
        raise ValueError(f"{variable} manquante dans le fichier .env")

    # Plusieurs clés séparées par des virgules dans la même variable
    return [cle.strip() for cle in valeur.split(",") if cle.strip()]


def get_client(usage: str = "agent", index_cle: int = 0) -> genai.Client:
    """
    Crée un client Gemini pour la clé n°index_cle de l'usage demandé.
    """
    cles = _obtenir_cles(usage)
    if index_cle >= len(cles):
        raise IndexError(f"Aucune clé restante pour l'usage '{usage}' (index {index_cle})")
    return genai.Client(api_key=cles[index_cle])


def send_message(
    contents,
    usage: str = "agent",
    tools=None,
    system_instruction=None,
    max_retries=3,
    reponse_json: bool = False,
):
    """
    Envoie une requête à Gemini, avec fallback automatique sur la clé
    suivante en cas de quota dépassé (429), et retry classique sur
    panne temporaire (503).

    reponse_json : si True, force Gemini à retourner du JSON pur
    (utile pour les réponses structurées comme get_meilleure_periode),
    sans avoir à parser d'éventuelles balises ```json parasites.
    """
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction=system_instruction,
        response_mime_type="application/json" if reponse_json else None,
    )

    cles = _obtenir_cles(usage)

    for index_cle in range(len(cles)):
        client = genai.Client(api_key=cles[index_cle])

        for attempt in range(max_retries):
            try:
                return client.models.generate_content(
                    model=MODEL_NAME,
                    contents=contents,
                    config=config,
                )
            except errors.ServerError:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    break  # passe à la clé suivante après épuisement des tentatives
            except errors.ClientError as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    print(f"Clé {index_cle + 1}/{len(cles)} épuisée pour '{usage}', tentative suivante...")
                    break  # sort de la boucle retry, passe à la clé suivante
                raise  # autre erreur client : on ne réessaie pas

    raise RuntimeError(
        f"Toutes les clés Gemini pour l'usage '{usage}' ont dépassé leur quota. "
        f"Réessaie plus tard (le quota se réinitialise généralement après 24h)."
    )