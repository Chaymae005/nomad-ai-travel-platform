"""
pipeline/extract_wikivoyage.py

Récupère le wikitext brut des pages Wikivoyage pour une liste de pays pilotes.
Stratégie : français en priorité, fallback anglais si la page fr n'existe pas
ou si son contenu est trop pauvre.

Sortie : un fichier JSON par pays dans data/raw/, contenant le wikitext brut
+ des métadonnées (langue utilisée, titre exact, date de récupération).
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# En dessous de ce nombre de caractères, on considère la page fr trop pauvre
# et on bascule sur la version anglaise.
MIN_CONTENT_LENGTH = 3000

HEADERS = {
    # Wikimedia demande un User-Agent identifiable, avec un contact.
    "User-Agent": "PFA-Voyage-Agent/1.0 (contact: chaymae@example.com)"
}

# slug interne -> (titre fr, titre en)
COUNTRIES = {
    "maroc":         ("Maroc", "Morocco"),
    "france":        ("France", "France"),
    "espagne":       ("Espagne", "Spain"),
    "italie":        ("Italie", "Italy"),
    "grece":         ("Grèce", "Greece"),
    "thailande":     ("Thaïlande", "Thailand"),
    "japon":         ("Japon", "Japan"),
    "etats_unis":    ("États-Unis", "United States of America"),
    "chine":         ("Chine", "China"),
    "bresil":        ("Brésil", "Brazil"),
    "egypte":        ("Égypte", "Egypt"),
    "turquie":       ("Turquie", "Turkey"),
    "australie":     ("Australie", "Australia"),
    "indonesie":     ("Indonésie", "Indonesia"),
    "inde":          ("Inde", "India"),
    "portugal":      ("Portugal", "Portugal"),
    "vietnam":       ("Vietnam", "Vietnam"),
    "coree_du_sud":  ("Corée du Sud", "South Korea"),
    "allemagne":     ("Allemagne", "Germany"),
    "mexique":       ("Mexique", "Mexico"),
    "perou":         ("Pérou", "Peru"),
    "afrique_du_sud":("Afrique du Sud", "South Africa"),
    "canada":        ("Canada", "Canada"),
    "suisse":        ("Suisse", "Switzerland"),
    "pays_bas":      ("Pays-Bas", "Netherlands"),
    "russie":        ("Russie", "Russia"),
    "royaume_uni":   ("Royaume-Uni", "United Kingdom"),
    "tunisie":       ("Tunisie", "Tunisia"),
    "kenya":         ("Kenya", "Kenya"),
    "tanzanie":      ("Tanzanie", "Tanzania"),
    "chili":         ("Chili", "Chile"),
    "colombie":      ("Colombie", "Colombia"),
    "argentine":     ("Argentine", "Argentina"),
    "nouvelle_zelande": ("Nouvelle-Zélande", "New Zealand"),
    "fidji":         ("Fidji", "Fiji"),
}


API_URLS = {
    "fr": "https://fr.wikivoyage.org/w/api.php",
    "en": "https://en.wikivoyage.org/w/api.php",
}


# ---------------------------------------------------------------------------
# Fonctions
# ---------------------------------------------------------------------------

def fetch_wikitext(title: str, lang: str) -> str | None:
    """
    Interroge l'API MediaWiki de Wikivoyage pour récupérer le wikitext brut
    de la dernière révision d'une page. Retourne None si la page n'existe pas.
    """
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvslots": "main",
        "rvprop": "content",
        "format": "json",
        "formatversion": "2",
        "redirects": 1,  # suit les redirections (ex: alias de nom de pays)
    }

    resp = requests.get(API_URLS[lang], params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None

    page = pages[0]
    if page.get("missing"):
        return None

    revisions = page.get("revisions")
    if not revisions:
        return None

    content = revisions[0]["slots"]["main"]["content"]
    return content


def extract_country(slug: str, title_fr: str, title_en: str) -> dict:
    """
    Récupère le wikitext pour un pays : essaie le français d'abord,
    bascule sur l'anglais si absent ou trop court.
    """
    wikitext_fr = fetch_wikitext(title_fr, "fr")

    if wikitext_fr and len(wikitext_fr) >= MIN_CONTENT_LENGTH:
        return {
            "slug": slug,
            "country": title_fr,
            "lang": "fr",
            "title_used": title_fr,
            "wikitext": wikitext_fr,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # Fallback anglais
    wikitext_en = fetch_wikitext(title_en, "en")
    if wikitext_en:
        return {
            "slug": slug,
            "country": title_fr,  # on garde le nom fr pour cohérence d'affichage
            "lang": "en",
            "title_used": title_en,
            "wikitext": wikitext_en,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # Ni fr ni en n'ont fonctionné
    return {
        "slug": slug,
        "country": title_fr,
        "lang": None,
        "title_used": None,
        "wikitext": None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "error": "Aucune page trouvée (fr et en)",
    }


def save_raw(slug: str, result: dict) -> Path:
    out_path = RAW_DIR / f"{slug}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return out_path


def main():
    print(f"Extraction de {len(COUNTRIES)} pays vers {RAW_DIR}/\n")

    for slug, (title_fr, title_en) in COUNTRIES.items():
        print(f"→ {slug} ...", end=" ")
        try:
            result = extract_country(slug, title_fr, title_en)
            save_raw(slug, result)

            if result["wikitext"]:
                n_chars = len(result["wikitext"])
                print(f"OK ({result['lang']}, {n_chars} caractères)")
            else:
                print(f"ÉCHEC — {result.get('error')}")

        except requests.RequestException as e:
            print(f"ERREUR RÉSEAU — {e}")

        # Petite pause pour rester poli avec l'API Wikimedia
        time.sleep(0.5)

    print("\nExtraction terminée.")


if __name__ == "__main__":
    main()