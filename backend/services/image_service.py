"""
services/image_service.py

Lit les images pré-générées par pipeline/recuperer_images.py.
Accepte n'importe quel nom de pays (anglais, français...) grâce à
resoudre_nom_pays_pour_rag, puisque images.json est indexé en français
comme le reste du contenu RAG.
"""

import json
from pathlib import Path
from agent.rag import resoudre_nom_pays_pour_rag

IMAGES_PATH = Path("data/curated/images.json")
IMAGE_FALLBACK = "/images/voyage.jpg"


def _charger_images() -> dict:
    if not IMAGES_PATH.exists():
        return {"pays": {}, "villes": {}}
    with open(IMAGES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_image_pays(nom_pays: str) -> str:
    images = _charger_images()
    nom_rag = resoudre_nom_pays_pour_rag(nom_pays)
    if nom_rag:
        return images["pays"].get(nom_rag, IMAGE_FALLBACK)
    return images["pays"].get(nom_pays, IMAGE_FALLBACK)


def get_image_ville(nom_ville: str) -> str:
    images = _charger_images()
    return images["villes"].get(nom_ville, IMAGE_FALLBACK)