"""
services/traductions.py

Table de correspondance français -> anglais pour les noms de pays,
partagée entre geo_service.py (recherche/navigation) et
country_service.py (page pays), pour éviter la désynchronisation
entre les deux. pycountry.search_fuzzy s'est révélé peu fiable sur
des noms français courants (ex: "maroc"), d'où cette table explicite.
"""

FRANCAIS_VERS_ANGLAIS = {
    "maroc": "Morocco", "egypte": "Egypt", "afrique du sud": "South Africa",
    "tunisie": "Tunisia", "kenya": "Kenya", "tanzanie": "Tanzania",
    "senegal": "Senegal", "namibie": "Namibia",
    "japon": "Japan", "thailande": "Thailand", "indonesie": "Indonesia",
    "inde": "India", "chine": "China", "vietnam": "Vietnam",
    "coree du sud": "South Korea", "turquie": "Turkey",
    "emirats arabes unis": "United Arab Emirates", "cambodge": "Cambodia",
    "sri lanka": "Sri Lanka", "philippines": "Philippines",
    "etats-unis": "United States", "etats unis": "United States",
    "canada": "Canada", "mexique": "Mexico",
    "bresil": "Brazil", "argentine": "Argentina", "perou": "Peru",
    "colombie": "Colombia", "chili": "Chile",
    "australie": "Australia", "nouvelle-zelande": "New Zealand",
    "nouvelle zelande": "New Zealand", "fidji": "Fiji",
    "france": "France", "italie": "Italy", "espagne": "Spain",
    "grece": "Greece", "portugal": "Portugal", "royaume-uni": "United Kingdom",
    "royaume uni": "United Kingdom", "allemagne": "Germany",
    "suisse": "Switzerland", "pays-bas": "Netherlands", "pays bas": "Netherlands",
    "autriche": "Austria", "croatie": "Croatia", "islande": "Iceland",
}


import unicodedata


def enlever_accents(texte: str) -> str:
    nfkd = unicodedata.normalize('NFKD', texte)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def normaliser_nom_pays(nom: str) -> str:
    """
    Convertit un nom de pays potentiellement en français vers son nom
    anglais canonique, pour les APIs qui attendent l'anglais (ex:
    countries.dev). Si le nom n'est pas dans la table (déjà en anglais,
    ou pays non couvert), le retourne inchangé.
    """
    normalise = enlever_accents(nom.strip())
    return FRANCAIS_VERS_ANGLAIS.get(normalise, nom)