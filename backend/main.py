"""
main.py

Point d'entrée FastAPI -- expose l'agent voyage et les services
(météo, pays, RAG) pour que le frontend React puisse les appeler.
"""
from auth.database import initialiser_base
from auth.routes import router as auth_router
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import types

from agent.orchestrator import ask_agent
from agent.tools_external import obtenir_meteo_ville
from services.country_service import get_country_page_data, get_meilleure_periode
from services.maps_service import get_coordonnees_ville, calculer_distance_trajet
from services.city_service import get_city_page_data, get_suggestions_restaurants
from services.search_service import rechercher
from services.geo_service import get_continents_populaires, get_pays_par_continent
from services.traveler_service import get_destinations_par_profil
from services.season_service import get_destinations_par_saison
from user_data.routes import router as user_data_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
initialiser_base()
app.include_router(auth_router)
app.include_router(user_data_router)


DESTINATIONS_POPULAIRES = ["Japan", "Italy", "France", "Morocco", "Spain", "Greece", "Thailand", "Egypt"]


def _history_json_vers_content(history_json: list) -> list:
    contents = []
    for item in history_json:
        contents.append(
            types.Content(role=item["role"], parts=[types.Part(text=item["text"])])
        )
    return contents


def _history_content_vers_json(history_content: list) -> list:
    history_json = []
    for content in history_content:
        textes = [part.text for part in content.parts if part.text]
        if textes:
            history_json.append({"role": content.role, "text": " ".join(textes)})
    return history_json


class AgentRequest(BaseModel):
    question: str
    history: list = []


class MeteoRequest(BaseModel):
    ville: str


@app.post("/agent/ask")
def route_ask_agent(request: AgentRequest):
    history_content = _history_json_vers_content(request.history) if request.history else []

    reponse, updated_history = ask_agent(request.question, history=history_content)

    return {
        "reponse": reponse,
        "history": _history_content_vers_json(updated_history),
    }


@app.post("/platform/meteo")
def route_meteo(request: MeteoRequest):
    return obtenir_meteo_ville(request.ville)


@app.get("/pays/{nom}")
def route_pays(nom: str):
    resultat = get_country_page_data(nom)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/pays/{nom}/saisons")
def route_pays_saisons(nom: str):
    resultat = get_meilleure_periode(nom)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/carte/{nom_ville}")
def route_coordonnees_ville(nom_ville: str):
    resultat = get_coordonnees_ville(nom_ville)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/trajet")
def route_trajet(depart: str, arrivee: str):
    resultat = calculer_distance_trajet(depart, arrivee)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/ville/{nom}")
def route_ville(nom: str, pays: str):
    resultat = get_city_page_data(nom, pays)
    return resultat


@app.get("/ville/{nom}/restaurants")
def route_ville_restaurants(nom: str, pays: str):
    resultat = get_suggestions_restaurants(nom, pays)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/recherche")
def route_recherche(q: str):
    resultat = rechercher(q)
    if "error" in resultat:
        raise HTTPException(status_code=404, detail=resultat["error"])
    return resultat


@app.get("/continents")
def route_continents():
    return get_continents_populaires()


@app.get("/continents/{nom}")
def route_continent(nom: str):
    pays_liste = get_pays_par_continent(nom)
    if pays_liste is None:
        raise HTTPException(status_code=404, detail=f"Continent inconnu : '{nom}'")
    return {"continent": nom, "pays": pays_liste}


@app.get("/voyageurs/{profil}")
def route_par_profil(profil: str):
    resultats = get_destinations_par_profil(profil)
    return {"profil": profil, "destinations": resultats}


@app.get("/saisons/{saison}")
def route_par_saison(saison: str):
    resultats = get_destinations_par_saison(saison)
    return {"saison": saison, "destinations": resultats}


@app.get("/destinations-populaires")
def route_destinations_populaires():
    return {"destinations": DESTINATIONS_POPULAIRES}


@app.get("/health")
def health():
    return {"status": "ok"}