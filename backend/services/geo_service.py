"""
services/geo_service.py

Base géographique complète (pays, continents, villes) via geonamescache,
utilisée pour la navigation et la recherche générale -- indépendante des
pays couverts par le RAG (qui servent seulement à enrichir le contenu
qualitatif quand disponible, voir agent/rag.py).
"""

import unicodedata
import geonamescache
from services.traductions import normaliser_nom_pays

_gc = geonamescache.GeonamesCache()

_CODES_CONTINENTS = {
    "AF": "Afrique", "AS": "Asie", "EU": "Europe",
    "NA": "Amérique du Nord", "SA": "Amérique du Sud",
    "OC": "Océanie", "AN": "Antarctique",
}


def get_continents() -> dict:
    """Retourne {continent: [liste de pays]} pour tous les continents."""
    pays_data = _gc.get_countries()
    resultat = {nom: [] for nom in _CODES_CONTINENTS.values()}

    for pays in pays_data.values():
        continent = _CODES_CONTINENTS.get(pays.get("continentcode"))
        if continent:
            resultat[continent].append(pays["name"])

    return resultat


# Sélection éditoriale des pays les plus connus touristiquement par
# continent, pour éviter d'afficher des pays peu pertinents pour une
# plateforme voyage grand public (ex: micro-états, pays en conflit).
# Contrairement à get_continents() qui liste tous les pays reconnus,
# cette liste est un choix manuel à ajuster selon la ligne éditoriale.
PAYS_POPULAIRES_PAR_CONTINENT = {
    "Europe": ["France", "Italy", "Spain", "Greece", "Portugal", "United Kingdom", "Germany", "Switzerland", "Netherlands", "Austria", "Croatia", "Iceland"],
    "Afrique": ["Morocco", "Egypt", "South Africa", "Tunisia", "Kenya", "Tanzania", "Senegal", "Namibia"],
    "Asie": ["Japan", "Thailand", "Indonesia", "India", "China", "Vietnam", "South Korea", "Turkey", "United Arab Emirates", "Cambodia", "Sri Lanka", "Philippines"],
    "Amérique du Nord": ["United States", "Canada", "Mexico"],
    "Amérique du Sud": ["Brazil", "Argentina", "Peru", "Colombia", "Chile"],
    "Océanie": ["Australia", "New Zealand", "Fiji"],
}


def get_continents_populaires() -> dict:
    """
    Comme get_continents(), mais filtré aux pays les plus connus
    touristiquement par continent -- pour la navigation grand public
    (dropdown Navbar, page Destinations), plutôt que la liste exhaustive.
    """
    tous_les_continents = get_continents()
    resultat = {}

    for continent, pays_selection in PAYS_POPULAIRES_PAR_CONTINENT.items():
        pays_reels = tous_les_continents.get(continent, [])
        resultat[continent] = [p for p in pays_selection if p in pays_reels]

    return resultat


def get_pays_par_continent(continent: str) -> list[str] | None:
    return get_continents_populaires().get(continent)


# Correspondance français -> anglais pour la recherche, limitée aux pays
# réellement utilisés dans l'app (PAYS_POPULAIRES_PAR_CONTINENT). Plus
# fiable que pycountry.search_fuzzy, qui échoue sur des noms français
# courants comme "maroc".
_FRANCAIS_VERS_ANGLAIS = {
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


def _enlever_accents(texte: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


# Correspondance pour les noms français courants des villes touristiques
_VILLES_FRANCAIS_VERS_ANGLAIS = {
    "barcelone": "Barcelona",
    "seville": "Seville",
    "séville": "Seville",
    "venise": "Venice",
    "marrakech": "Marrakesh",
    "fes": "Fes",
    "fès": "Fes",
    "athenes": "Athens",
    "athènes": "Athens",
    "santorin": "Santorini",
    "mykonos": "Mykonos",
    "le caire": "Cairo",
    "caire": "Cairo",
    "louxor": "Luxor",
    "alexandrie": "Alexandria",
    "cappadoce": "Goreme",
    "pekin": "Beijing",
    "pékin": "Beijing",
    "xi'an": "Xi'an",
    "xian": "Xi'an",
    "new york": "New York City",
    "florence": "Florence",
    "moulay yacoub": "Moulay Yacoub",
    "chefchaouen": "Chefchaouene",
}


def rechercher_pays(nom: str) -> str | None:
    normalise = _enlever_accents(nom.strip())

    # 1. Essai direct sur le nom anglais (geonamescache)
    for pays in _gc.get_countries().values():
        if _enlever_accents(pays["name"]) == normalise:
            return pays["name"]

    # 2. Essai via la table de correspondance française
    nom_anglais = _FRANCAIS_VERS_ANGLAIS.get(normalise)
    if nom_anglais:
        for pays in _gc.get_countries().values():
            if _enlever_accents(pays["name"]) == _enlever_accents(nom_anglais):
                return pays["name"]

    return None


def rechercher_ville(nom: str) -> dict | None:
    """Retourne {nom, pays, latitude, longitude} pour la ville la plus peuplée correspondant au nom."""
    if not nom or not str(nom).strip():
        return None

    nom_nettoye = str(nom).strip()
    candidats = [nom_nettoye]

    # Alias français -> anglais pour les villes courantes
    nom_fr_norm = _enlever_accents(nom_nettoye)
    alias_en = _VILLES_FRANCAIS_VERS_ANGLAIS.get(nom_fr_norm)
    if alias_en and alias_en not in candidats:
        candidats.append(alias_en)

    # Si la ville contient une virgule ou précision (ex: "Washington, D.C.")
    if "," in nom_nettoye:
        avant_virgule = nom_nettoye.split(",")[0].strip()
        if avant_virgule not in candidats:
            candidats.append(avant_virgule)

    # 1. Recherche directe dans geonamescache
    for c in candidats:
        correspondances = _gc.get_cities_by_name(c)
        if correspondances:
            toutes = [ville for match in correspondances for ville in match.values()]
            meilleure = max(toutes, key=lambda v: v.get("population", 0))
            code_pays = meilleure.get("countrycode")
            pays_data = _gc.get_countries().get(code_pays, {})
            return {
                "nom": meilleure["name"],
                "pays": pays_data.get("name", code_pays),
                "latitude": meilleure["latitude"],
                "longitude": meilleure["longitude"],
            }

    # 2. Fallback accent-insensible (ex: Brasilia -> Brasília, Bogota -> Bogotá, Reykjavik -> Reykjavík)
    for c in candidats:
        norm_c = _enlever_accents(c)
        correspondances_norm = [
            v for v in _gc.get_cities().values()
            if _enlever_accents(v["name"]) == norm_c
        ]
        if correspondances_norm:
            meilleure = max(correspondances_norm, key=lambda v: v.get("population", 0))
            code_pays = meilleure.get("countrycode")
            pays_data = _gc.get_countries().get(code_pays, {})
            return {
                "nom": meilleure["name"],
                "pays": pays_data.get("name", code_pays),
                "latitude": meilleure["latitude"],
                "longitude": meilleure["longitude"],
            }

    return None


def obtenir_coordonnees_destination(nom: str, type_destination: str = "pays") -> dict | None:
    """
    Retourne {'latitude': float, 'longitude': float} pour n'importe quelle destination
    (pays ou ville, en français ou en anglais).
    """
    if not nom or not str(nom).strip():
        return None

    nom_propre = str(nom).strip()

    if type_destination == "ville":
        ville = rechercher_ville(nom_propre)
        if ville:
            return {"latitude": ville["latitude"], "longitude": ville["longitude"]}
        # Fallback géocodage Open-Meteo
        try:
            import requests
            r = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": nom_propre, "count": 1},
                timeout=5,
            ).json()
            results = r.get("results")
            if results:
                return {"latitude": results[0]["latitude"], "longitude": results[0]["longitude"]}
        except Exception:
            pass
        return None

    # type_destination == "pays"
    nom_en = normaliser_nom_pays(nom_propre)

    # 1. Recherche de la capitale via geonamescache local (instantané & hors ligne)
    nom_norm = _enlever_accents(nom_propre)
    nom_en_norm = _enlever_accents(nom_en)
    for c in _gc.get_countries().values():
        c_name_norm = _enlever_accents(c["name"])
        if c_name_norm in [nom_norm, nom_en_norm]:
            capitale = c.get("capital")
            if capitale:
                ville = rechercher_ville(capitale)
                if ville:
                    return {"latitude": ville["latitude"], "longitude": ville["longitude"]}
            break

    # 2. Fallback via get_country_info
    try:
        from agent.tools_external import get_country_info
        info = get_country_info(nom_en)
        if "error" not in info and info.get("capital") and info["capital"] != "Inconnu":
            ville = rechercher_ville(info["capital"])
            if ville:
                return {"latitude": ville["latitude"], "longitude": ville["longitude"]}
    except Exception:
        pass

    # 3. Fallback géocodage Open-Meteo pour le pays
    try:
        import requests
        r = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": nom_en, "count": 1},
            timeout=5,
        ).json()
        results = r.get("results")
        if results:
            return {"latitude": results[0]["latitude"], "longitude": results[0]["longitude"]}
    except Exception:
        pass

    return None