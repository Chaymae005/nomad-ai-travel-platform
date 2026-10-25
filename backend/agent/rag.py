import pycountry
import chromadb
from pipeline.extract_wikivoyage import COUNTRIES  # source unique de vérité : slug -> (nom_fr, nom_en)

VECTORSTORE_DIR = "vectorstore"
COLLECTION_NAME = "wikivoyage_pays"
SEUIL_DISTANCE_MAX = 0.55

_client = chromadb.PersistentClient(path=VECTORSTORE_DIR)
_collection = _client.get_collection(COLLECTION_NAME)


def enlever_accents(texte: str) -> str:
    remplacements = str.maketrans("éèêëàâäùûüôöîïç", "eeeeaaauuuooiic")
    return texte.lower().translate(remplacements)


# --- Détection texte libre (pour l'agent conversationnel / Gemini) ---
_PAYS_MONDE = {}
for pays in pycountry.countries:
    _PAYS_MONDE[enlever_accents(pays.name)] = pays.name
    if hasattr(pays, "common_name"):
        _PAYS_MONDE[enlever_accents(pays.common_name)] = pays.common_name

for slug, (nom_fr, nom_en) in COUNTRIES.items():
    _PAYS_MONDE[enlever_accents(nom_fr)] = nom_fr


def detecter_pays_dans_texte(texte: str) -> str | None:
    normalise = enlever_accents(texte)
    for cle, nom in _PAYS_MONDE.items():
        if cle in normalise:
            return nom
    return None


# --- Résolution fiable par code ISO (pour les services qui connaissent déjà le pays) ---
def _construire_correspondance_codes() -> dict:
    correspondance = {}
    for slug, (nom_fr, nom_en) in COUNTRIES.items():
        try:
            pays = pycountry.countries.search_fuzzy(nom_en)[0]
            correspondance[pays.alpha_2] = nom_fr
        except LookupError:
            continue
    return correspondance


_CODE_VERS_NOM_FR = _construire_correspondance_codes()


def resoudre_nom_pays_pour_rag(nom_pays: str) -> str | None:
    """
    Convertit un nom de pays (n'importe quelle langue/graphie, ex: 'Japan',
    'JP', 'Japon') vers le nom français exact stocké dans les métadonnées
    RAG, via son code ISO. Retourne None si le pays n'est pas reconnu ou
    pas indexé dans le pipeline (COUNTRIES) -- ce None doit être traité
    comme "pas de RAG disponible", proprement, par l'appelant.
    """
    from services.traductions import normaliser_nom_pays
    nom_normalise = normaliser_nom_pays(nom_pays)
    try:
        pays = pycountry.countries.search_fuzzy(nom_normalise)[0]
    except LookupError:
        return None
    return _CODE_VERS_NOM_FR.get(pays.alpha_2)


def get_pays_indexes() -> set:
    tous_les_metadatas = _collection.get(include=["metadatas"])["metadatas"]
    return {m["country"] for m in tous_les_metadatas if m.get("country")}


_PAYS_INDEXES = get_pays_indexes()


def search_rag(query: str, category: str = None, n_results: int = 3, country: str | None = None) -> dict:
    """
    country : nom français déjà résolu (via resoudre_nom_pays_pour_rag),
    à utiliser quand l'appelant connaît déjà le pays exact. Si absent,
    on retombe sur la détection texte libre (usage agent/Gemini).
    """
    filtre = {"category": category} if category else None

    resultats = _collection.query(
        query_texts=[query], n_results=n_results, where=filtre,
        include=["documents", "metadatas", "distances"],
    )

    documents = resultats.get("documents", [[]])[0]
    metadatas = resultats.get("metadatas", [[]])[0]
    distances = resultats.get("distances", [[]])[0]

    pays_demande = country if country else detecter_pays_dans_texte(query)

    if pays_demande and pays_demande not in _PAYS_INDEXES:
        return {"error": f"Aucune information disponible sur {pays_demande} dans la base."}

    passages = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist > SEUIL_DISTANCE_MAX:
            continue
        if pays_demande and meta.get("country") != pays_demande:
            continue
        passages.append({
            "country": meta.get("country"), "section": meta.get("section"),
            "category": meta.get("category"), "text": doc,
        })

    if not passages:
        return {"error": "Aucun passage suffisamment pertinent trouvé dans la base Wikivoyage."}

    return {"passages": passages, "source": "Wikivoyage (base RAG)"}