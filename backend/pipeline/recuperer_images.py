"""
pipeline/recuperer_images.py

Récupère une image représentative pour chaque pays et chaque ville
populaire, via l'API Wikipedia (pageimages) -- plus fiable que des
banques d'images génériques pour du contenu voyage réel.

Exécuté une seule fois : le résultat est stocké dans data/curated/images.json,
et lu tel quel par le backend, sans appel réseau à chaque visite de page.
"""

import json
import requests
from pathlib import Path
from pipeline.extract_wikivoyage import COUNTRIES
from services.country_service import VILLES_POPULAIRES

CURATED_DIR = Path("data/curated")
CURATED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = CURATED_DIR / "images.json"

WIKIPEDIA_API_URL = "https://{langue}.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "PFA-Voyage-Agent/1.0 (contact: chaymae@example.com)"}


def recuperer_image_wikipedia(titre: str, langue: str = "fr") -> str | None:
    """Récupère l'image principale d'une page Wikipedia, haute résolution."""
    params = {
        "action": "query",
        "prop": "pageimages",
        "titles": titre,
        "piprop": "original",
        "format": "json",
        "formatversion": "2",
        "redirects": 1,
    }

    try:
        response = requests.get(WIKIPEDIA_API_URL.format(langue=langue), params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    pages = data.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return None

    original = pages[0].get("original")
    return original.get("source") if original else None


def recuperer_image(titre_fr: str, titre_en: str) -> str | None:
    """Essaie le français d'abord, puis l'anglais en secours."""
    image = recuperer_image_wikipedia(titre_fr, "fr")
    if image:
        return image
    return recuperer_image_wikipedia(titre_en, "en")


def main():
    resultats = {"pays": {}, "villes": {}}

    print(f"Récupération des images pour {len(COUNTRIES)} pays...\n")
    for slug, (titre_fr, titre_en) in COUNTRIES.items():
        print(f"→ {titre_fr} ...", end=" ")
        image = recuperer_image(titre_fr, titre_en)
        if image:
            resultats["pays"][titre_fr] = image
            print("OK")
        else:
            print("aucune image trouvée")

    toutes_les_villes = [ville for liste in VILLES_POPULAIRES.values() for ville in liste]
    print(f"\nRécupération des images pour {len(toutes_les_villes)} villes...\n")
    for ville in toutes_les_villes:
        print(f"→ {ville} ...", end=" ")
        image = recuperer_image(ville, ville)
        if image:
            resultats["villes"][ville] = image
            print("OK")
        else:
            print("aucune image trouvée")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print(f"\n{len(resultats['pays'])} pays et {len(resultats['villes'])} villes sauvegardés dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()