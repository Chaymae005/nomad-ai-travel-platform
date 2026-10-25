"""
pipeline/generer_tags_voyageurs.py

Pour chaque pays indexé dans le RAG, demande à Gemini de juger --
à partir du contenu Wikivoyage réel de ce pays -- si le pays convient
à un voyage en famille, en couple, entre amis, ou solo, avec justification.

Exécuté une seule fois (ou à chaque mise à jour du RAG), pas à chaque
visite de page : le résultat est stocké dans data/curated/, et lu tel
quel par le backend. Le script décide seul ; aucune présélection manuelle.
"""

import json
from pathlib import Path
from google.genai import types
from gemini.client import send_message
from agent.rag import search_rag, get_pays_indexes

CURATED_DIR = Path("data/curated")
CURATED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = CURATED_DIR / "tags_voyageurs.json"

INSTRUCTION = (
    "Tu es un expert voyage. À partir du contexte fourni sur un pays "
    "(climat, activités, sécurité, infrastructure, ambiance), évalue si "
    "ce pays convient à chacun de ces 4 profils de voyageurs : famille "
    "(avec enfants et/ou personnes âgées), couple, groupe d'amis, solo.\n\n"
    "Base-toi UNIQUEMENT sur les informations du contexte fourni. Si le "
    "contexte ne permet pas de juger un profil précis, donne une "
    "évaluation prudente ('moyen') plutôt que d'inventer un détail non "
    "mentionné.\n\n"
    "Réponds STRICTEMENT en JSON avec cette structure exacte :\n"
    "{\n"
    '  "famille": {"recommandation": "ideal|bon|moyen|deconseille", "justification": "..."},\n'
    '  "couple": {"recommandation": "...", "justification": "..."},\n'
    '  "amis": {"recommandation": "...", "justification": "..."},\n'
    '  "solo": {"recommandation": "...", "justification": "..."}\n'
    "}\n"
    "Chaque justification doit être concise (1-2 phrases max), factuelle, "
    "sans généralité vague."
)


def construire_contexte_pays(nom_pays_fr: str) -> str | None:
    """Rassemble le contenu RAG pertinent (tourisme + général) pour un pays."""
    rag_tourisme = search_rag(
        f"climat, activités et sécurité pour voyager en {nom_pays_fr}",
        category="tourisme",
        country=nom_pays_fr,
    )
    rag_general = search_rag(
        f"présentation générale de {nom_pays_fr}",
        category="general",
        country=nom_pays_fr,
    )

    passages = []
    if "error" not in rag_tourisme:
        passages += [p["text"] for p in rag_tourisme["passages"]]
    if "error" not in rag_general:
        passages += [p["text"] for p in rag_general["passages"]]

    if not passages:
        return None
    return "\n\n".join(passages)


def juger_pays(nom_pays_fr: str) -> dict | None:
    contexte = construire_contexte_pays(nom_pays_fr)
    if contexte is None:
        print(f"  → pas assez de contenu RAG, ignoré")
        return None

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Contexte sur {nom_pays_fr} :\n{contexte}")],
        )
    ]

    response = send_message(
     contents=contents,
     usage="voyageurs",
     system_instruction=INSTRUCTION,
     reponse_json=True,
)

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, AttributeError):
        print(f"  → réponse Gemini invalide, ignoré")
        return None


def main():
    pays_indexes = sorted(get_pays_indexes())
    print(f"{len(pays_indexes)} pays à traiter.\n")

    resultats = {}
    for nom_pays in pays_indexes:
        print(f"→ {nom_pays} ...", end=" ")
        jugement = juger_pays(nom_pays)
        if jugement:
            resultats[nom_pays] = jugement
            print("OK")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print(f"\n{len(resultats)} pays traités, sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()