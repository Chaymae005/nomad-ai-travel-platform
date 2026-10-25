"""
pipeline/generer_presentations.py

Génère ou met à jour les présentations courtes, vivantes et amicales
pour chaque destination dans data/curated/presentations.json.
Peut être relancé si de nouveaux pays sont ajoutés.
"""

import json
from pathlib import Path
from gemini.client import send_message
from pipeline.extract_wikivoyage import COUNTRIES
from services.geo_service import PAYS_POPULAIRES_PAR_CONTINENT

CURATED_DIR = Path("data/curated")
CURATED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = CURATED_DIR / "presentations.json"

PROMPT_TEMPLATE = (
    "Tu es un guide voyage passionné et bienveillant. Rédige une présentation courte, vivante et amicale pour la page destination d'un pays : {nom}.\n"
    "Contraintes :\n"
    "- 1 à 2 courts paragraphes (environ 100 à 130 mots au total).\n"
    "- Mentionne naturellement sa situation géographique (où il se trouve, bordé par quoi, pays voisins).\n"
    "- Mentionne son nom local et comment les habitants l'appellent ou le prononcent.\n"
    "- Mentionne sa monnaie.\n"
    "- Évoque son histoire et son ambiance culturelle/mode de vie de manière chaleureuse.\n"
    "- Rédige dans un style fluide, amical et invitant au voyage, sans puces ni titres techniques."
)


def charger_existant() -> dict:
    if OUTPUT_PATH.exists():
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def generer_presentation(nom_pays: str) -> str:
    prompt = PROMPT_TEMPLATE.format(nom=nom_pays)
    res = send_message(prompt, usage="agent")
    return res.text.strip()


def main():
    presentations = charger_existant()
    pays_cibles = set()

    for slug, (nom_fr, nom_en) in COUNTRIES.items():
        pays_cibles.add(nom_fr)

    for liste in PAYS_POPULAIRES_PAR_CONTINENT.values():
        for p in liste:
            pays_cibles.add(p)

    print(f"Total pays à vérifier : {len(pays_cibles)}")

    ajouts = 0
    for nom in sorted(pays_cibles):
        if nom not in presentations:
            print(f"Génération pour {nom}...")
            try:
                texte = generer_presentation(nom)
                if texte:
                    presentations[nom] = texte
                    ajouts += 1
                    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                        json.dump(presentations, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erreur pour {nom} : {e}")
        else:
            print(f"Déjà présent : {nom}")

    print(f"Terminé. {ajouts} nouvelles présentations générées. Total : {len(presentations)}")


if __name__ == "__main__":
    main()
