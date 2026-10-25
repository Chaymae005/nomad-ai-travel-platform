"""
pipeline/chunk_and_embed.py

Découpe les sections nettoyées (data/processed/) en chunks, génère leurs
embeddings, et les stocke dans une base vectorielle Chroma persistante
(vectorstore/).

Ce script ne fait AUCUN appel réseau vers Gemini — Chroma génère les
embeddings localement via sentence-transformers (déjà dans requirements.txt).
"""

import json
from pathlib import Path

import chromadb

PROCESSED_DIR = Path("data/processed")
VECTORSTORE_DIR = Path("vectorstore")

COLLECTION_NAME = "wikivoyage_pays"


def construire_chunks() -> list[dict]:
    """
    Parcourt tous les fichiers nettoyés et construit la liste des chunks
    à indexer. Un chunk = une section d'un pays, avec le nom du pays
    inclus dans le texte pour ne jamais perdre le contexte.
    """
    chunks = []

    for fichier in PROCESSED_DIR.glob("*.json"):
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)

        pays = data["country"]

        for section in data.get("sections", []):
            # On préfixe le texte avec le pays et la section, pour que
            # la recherche par similarité retrouve bien le bon contexte
            # même si le pays n'est pas répété plusieurs fois dans le texte.
            texte_avec_contexte = (
                f"Pays : {pays}\nSection : {section['section']}\n\n{section['text']}"
            )

            chunk_id = f"{data['slug']}__{section['section']}".lower().replace(" ", "_")

            chunks.append({
                "id": chunk_id,
                "text": texte_avec_contexte,
                "metadata": {
                    "country": pays,
                    "section": section["section"],
                    "category": section.get("category", "general"),
                    "slug": data["slug"],
                },
            })

    return chunks


def main():
    chunks = construire_chunks()
    print(f"{len(chunks)} chunks à indexer.\n")

    # Client Chroma persistant : les données survivent entre deux lancements
    client = chromadb.PersistentClient(path=str(VECTORSTORE_DIR))

    # On repart d'une collection propre à chaque exécution du pipeline,
    # pour éviter d'accumuler des doublons si on relance plusieurs fois.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # la collection n'existait pas encore, rien à faire

    # NOUVEAU : métrique de similarité cosinus explicite, plutôt que
    # de laisser Chroma sur son défaut L2 — plus stable pour du texte.
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )

    print(f"Indexation terminée dans {VECTORSTORE_DIR}/ (collection: {COLLECTION_NAME})")


if __name__ == "__main__":
    main()