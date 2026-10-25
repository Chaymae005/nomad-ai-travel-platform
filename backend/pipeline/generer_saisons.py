"""
pipeline/generer_saisons.py

Pour chaque pays indexé dans le RAG, demande à Gemini de juger --
à partir du contenu Wikivoyage réel de ce pays -- la meilleure période
pour y voyager, saison par saison, avec justification.

Exécuté une seule fois (ou à chaque mise à jour du RAG), pas à chaque
visite de page : le résultat est stocké dans data/curated/, et lu tel
quel par le backend.

Combine deux requêtes RAG (climat + présentation générale) plutôt
qu'une seule requête étroite, pour éviter de rater le seuil de
similarité sur des pays dont le contenu climat est formulé différemment.

Sauvegarde progressivement après chaque pays traité, et reprend
automatiquement là où il s'est arrêté si relancé (utile en cas de
quota Gemini épuisé en cours de route).
"""

import json
from pathlib import Path
from google.genai import types
from gemini.client import send_message
from agent.rag import search_rag, get_pays_indexes

CURATED_DIR = Path("data/curated")
CURATED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = CURATED_DIR / "saisons.json"

INSTRUCTION = (
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


def construire_contexte_climat(nom_pays_fr: str) -> str | None:
    """
    Rassemble le contenu RAG pertinent pour juger les saisons : climat
    (catégorie tourisme) + présentation générale, à l'image de
    generer_tags_voyageurs.py, pour ne pas dépendre d'une seule requête
    étroite qui peut rater le seuil de similarité.
    """
    rag_climat = search_rag(
        f"climat et meilleure période pour voyager en {nom_pays_fr}",
        category="tourisme",
        country=nom_pays_fr,
    )
    rag_general = search_rag(
        f"présentation générale et géographie de {nom_pays_fr}",
        category="general",
        country=nom_pays_fr,
    )

    passages = []
    if "error" not in rag_climat:
        passages += [p["text"] for p in rag_climat["passages"]]
    if "error" not in rag_general:
        passages += [p["text"] for p in rag_general["passages"]]

    if not passages:
        return None
    return "\n\n".join(passages)


def juger_saisons(nom_pays_fr: str) -> dict | None:
    contexte = construire_contexte_climat(nom_pays_fr)
    if contexte is None:
        print("  → pas assez de contenu RAG, ignoré")
        return None

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"Contexte sur {nom_pays_fr} :\n{contexte}")],
        )
    ]

    response = send_message(
        contents=contents,
        usage="saisons",
        system_instruction=INSTRUCTION,
        reponse_json=True,
    )

    try:
        return json.loads(response.text)
    except (json.JSONDecodeError, AttributeError):
        print("  → réponse Gemini invalide, ignoré")
        return None


def main():
    pays_indexes = sorted(get_pays_indexes())
    print(f"{len(pays_indexes)} pays à traiter.\n", flush=True)

    resultats = {}
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            resultats = json.load(f)
        print(f"{len(resultats)} pays déjà traités précédemment, reprise en cours.\n", flush=True)

    for nom_pays in pays_indexes:
        if nom_pays in resultats:
            print(f"→ {nom_pays} ... déjà fait, ignoré", flush=True)
            continue

        print(f"→ {nom_pays} ...", end=" ", flush=True)

        try:
            jugement = juger_saisons(nom_pays)
        except RuntimeError:
            print("\n\nQuota épuisé, arrêt du script. Relance plus tard pour continuer où on s'est arrêté.", flush=True)
            break

        if jugement:
            resultats[nom_pays] = jugement
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(resultats, f, ensure_ascii=False, indent=2)
            print("OK", flush=True)

    print(f"\n{len(resultats)} pays traités au total, sauvegardés dans {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()