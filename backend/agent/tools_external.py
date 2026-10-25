import requests
import os
from services.geo_service import rechercher_ville
from services.traductions import normaliser_nom_pays


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float, city_name: str = "") -> dict:
    """
    Récupère un ensemble complet de données météo pour une ville :
    - la météo actuelle
    - les prévisions horaires pour les prochaines 48h (utile si l'utilisateur précise une heure)
    - les prévisions journalières pour les 7 prochains jours (utile pour "demain", "ce week-end"...)

    L'agent (Gemini) se charge ensuite de sélectionner, dans ces données,
    l'information exacte qui correspond à la question posée.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "hourly": "temperature_2m,weathercode,windspeed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
        "forecast_days": 7,
        "timezone": "auto",  # Open-Meteo déduit le fuseau horaire local à partir des coordonnées
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Impossible de récupérer la météo : {e}"}

    data = response.json()

    return {
        "city": city_name or f"({latitude}, {longitude})",
        "timezone": data.get("timezone"),
        "current": data.get("current_weather", {}),
        "hourly_forecast": data.get("hourly", {}),
        "daily_forecast": data.get("daily", {}),
        "source": "Open-Meteo API",
    }



COUNTRIES_DEV_URL = "https://countries.dev/name"


def get_country_info(country_name: str) -> dict:
    """
    Appelle l'API countries.dev (alternative gratuite et sans clé à
    RestCountries, dont l'ancienne version v3.1 a été retirée) pour
    récupérer des informations structurées et fiables sur un pays.
    """
    country_name_en = normaliser_nom_pays(country_name)
    url = f"{COUNTRIES_DEV_URL}/{country_name_en}"

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        return {"error": f"Impossible de récupérer les informations du pays : {e}"}

    if response.status_code == 404:
        return {
            "error": (
                f"Aucun pays trouvé pour '{country_name}'. "
                "Réessaie avec le nom du pays en anglais (ex: 'Morocco' plutôt que 'Maroc')."
            )
        }

    if response.status_code != 200:
        return {"error": f"Erreur de l'API countries.dev (code {response.status_code})"}

    data = response.json()
    if not isinstance(data, list) or len(data) == 0:
        return {"error": f"Aucun pays trouvé pour '{country_name}'."}

    # Sélectionne la correspondance exacte ou le pays le plus peuplé
    country = next(
        (c for c in data if c.get("name", "").lower() == country_name_en.lower()),
        None,
    )
    if not country:
        country = max(data, key=lambda c: c.get("population") or 0)

    # Extraction propre de la capitale (peut être str, list ou None)
    raw_capital = country.get("capital")
    if isinstance(raw_capital, list):
        capitale = raw_capital[0] if raw_capital else "Inconnu"
    elif isinstance(raw_capital, str) and raw_capital.strip():
        capitale = raw_capital.strip()
    else:
        capitale = "Inconnu"

    if capitale == "Inconnu":
        from services.geo_service import _gc
        for c in _gc.get_countries().values():
            if c["name"].lower() == country_name_en.lower() or c.get("iso", "").lower() == str(country.get("alpha2Code", "")).lower():
                if c.get("capital"):
                    capitale = c["capital"]
                    break

    return {
        "name": country.get("name"),
        "capital": capitale,
        "region": country.get("region"),
        "subregion": country.get("subregion"),
        "population": country.get("population"),
        "area_km2": country.get("area"),
        "languages": [lang.get("name") for lang in country.get("languages", [])],
        "currencies": [cur.get("code") for cur in country.get("currencies", [])],
        "flag_emoji": country.get("flag"),
        "flag_url": country.get("flags", {}).get("png"),
        "maps_url": country.get("maps", {}).get("googleMaps"),
        "source": "countries.dev API",
    }




WIKIPEDIA_API_URL = "https://{langue}.wikipedia.org/api/rest_v1/page/summary/{sujet}"


def get_wikipedia_summary(sujet: str, langue: str = "fr") -> dict:
    """
    Récupère un résumé encyclopédique sur n'importe quel sujet via
    l'API REST officielle de Wikipedia (gratuite, sans clé).
    """
    url = WIKIPEDIA_API_URL.format(langue=langue, sujet=sujet.replace(" ", "_"))

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        return {"error": f"Impossible de contacter Wikipedia : {e}"}

    if response.status_code == 404:
        # Essaie automatiquement en anglais si la version demandée n'existe pas
        if langue == "fr":
            return get_wikipedia_summary(sujet, langue="en")
        return {"error": f"Aucun article Wikipedia trouvé pour '{sujet}'."}

    if response.status_code != 200:
        return {"error": f"Erreur de l'API Wikipedia (code {response.status_code})"}

    data = response.json()

    return {
        "titre": data.get("title"),
        "resume": data.get("extract"),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        "image_url": data.get("thumbnail", {}).get("source"),
        "source": "Wikipedia",
    }

PEXELS_API_URL = "https://api.pexels.com/v1/search"

def rechercher_image(requete: str) -> str:
    """Retourne l'URL d'une image pertinente via Pexels, ou une image de secours."""
    cle = os.getenv("PEXELS_API_KEY")
    if not cle:
        return "/images/voyage.jpg"

    try:
        response = requests.get(
            PEXELS_API_URL,
            headers={"Authorization": cle},
            params={"query": requete, "per_page": 1},
            timeout=8,
        )
        data = response.json()
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["medium"]
    except requests.RequestException:
        pass

    return "/images/voyage.jpg"



def obtenir_meteo_ville(nom_ville: str) -> dict:
    ville = rechercher_ville(nom_ville)
    if ville is None:
        return {"error": f"Ville introuvable : '{nom_ville}'"}
    return get_weather(latitude=ville["latitude"], longitude=ville["longitude"], city_name=ville["nom"])






GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

def obtenir_meteo_ville(nom_ville: str) -> dict:
    """Convertit un nom de ville en coordonnées puis récupère la météo, en un seul appel pratique."""
    try:
        geo = requests.get(GEOCODING_URL, params={"name": nom_ville, "count": 1}, timeout=8)
        geo_data = geo.json()
        resultats = geo_data.get("results")
        if not resultats:
            return {"error": f"Ville introuvable : '{nom_ville}'"}

        lat = resultats[0]["latitude"]
        lon = resultats[0]["longitude"]
        meteo = get_weather(latitude=lat, longitude=lon, city_name=nom_ville)
        return meteo
    except requests.RequestException as e:
        return {"error": f"Impossible de géocoder '{nom_ville}' : {e}"}