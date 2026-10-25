"""
user_data/routes.py

Routes pour l'espace utilisateur : favoris, historique de recherche,
itinéraires sauvegardés, préférences, recommandations.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.database import get_db, Utilisateur, Favori, RechercheHistorique, Itineraire
from auth.dependencies import get_current_user
from services.recommendation_service import recommander_destinations
from agent.tools_external import get_country_info
from services.geo_service import rechercher_ville, obtenir_coordonnees_destination

router = APIRouter(prefix="/user", tags=["user_data"])


# ---------- FAVORIS ----------

class FavoriRequest(BaseModel):
    type_destination: str  # "pays" ou "ville"
    nom: str


@router.post("/favoris")
def ajouter_favori(
    request: FavoriRequest,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    existant = db.query(Favori).filter(
        Favori.user_id == user.id, Favori.nom == request.nom
    ).first()
    if existant:
        raise HTTPException(status_code=400, detail="Déjà dans les favoris.")

    favori = Favori(user_id=user.id, type_destination=request.type_destination, nom=request.nom)
    db.add(favori)
    db.commit()
    db.refresh(favori)
    return {"id": favori.id, "nom": favori.nom, "type_destination": favori.type_destination}


@router.get("/favoris")
def lister_favoris(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    favoris = db.query(Favori).filter(Favori.user_id == user.id).all()
    return [
        {"id": f.id, "nom": f.nom, "type_destination": f.type_destination}
        for f in favoris
    ]


@router.get("/favoris/verifier")
def verifier_favori(
    nom: str,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    """Vérifie si un élément est déjà en favori, pour afficher le cœur plein au chargement de la page."""
    favori = db.query(Favori).filter(Favori.user_id == user.id, Favori.nom == nom).first()
    return {"est_favori": favori is not None, "favori_id": favori.id if favori else None}


@router.get("/favoris/carte")
def carte_favoris(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    favoris = db.query(Favori).filter(Favori.user_id == user.id).all()
    points = []

    for f in favoris:
        coords = obtenir_coordonnees_destination(f.nom, f.type_destination)
        if coords:
            points.append({
                "nom": f.nom,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
            })

    return {"points": points}

@router.delete("/favoris/{favori_id}")
def supprimer_favori(
    favori_id: int,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    favori = db.query(Favori).filter(Favori.id == favori_id, Favori.user_id == user.id).first()
    if not favori:
        raise HTTPException(status_code=404, detail="Favori introuvable.")

    db.delete(favori)
    db.commit()
    return {"ok": True}


# ---------- HISTORIQUE ----------

class HistoriqueRequest(BaseModel):
    terme_recherche: str


@router.post("/historique")
def ajouter_historique(
    request: HistoriqueRequest,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    entree = RechercheHistorique(user_id=user.id, terme_recherche=request.terme_recherche)
    db.add(entree)
    db.commit()
    db.refresh(entree)
    return entree


@router.get("/historique")
def lister_historique(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    return (
        db.query(RechercheHistorique)
        .filter(RechercheHistorique.user_id == user.id)
        .order_by(RechercheHistorique.date_recherche.desc())
        .limit(50)
        .all()
    )


@router.delete("/historique")
def vider_historique(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    db.query(RechercheHistorique).filter(RechercheHistorique.user_id == user.id).delete()
    db.commit()
    return {"ok": True}


# ---------- ITINÉRAIRES ----------

class ItineraireRequest(BaseModel):
    titre: str
    etapes: list[dict]


@router.post("/itineraires")
def sauvegarder_itineraire(
    request: ItineraireRequest,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    itineraire = Itineraire(
        user_id=user.id,
        titre=request.titre,
        contenu_json=json.dumps(request.etapes),
    )
    db.add(itineraire)
    db.commit()
    db.refresh(itineraire)
    return {**itineraire.__dict__, "etapes": request.etapes}


@router.get("/itineraires")
def lister_itineraires(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    itineraires = db.query(Itineraire).filter(Itineraire.user_id == user.id).all()
    resultat = []
    for it in itineraires:
        resultat.append({
            "id": it.id,
            "titre": it.titre,
            "etapes": json.loads(it.contenu_json),
            "date_creation": it.date_creation,
        })
    return resultat


@router.delete("/itineraires/{itineraire_id}")
def supprimer_itineraire(
    itineraire_id: int,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    itineraire = db.query(Itineraire).filter(
        Itineraire.id == itineraire_id, Itineraire.user_id == user.id
    ).first()
    if not itineraire:
        raise HTTPException(status_code=404, detail="Itinéraire introuvable.")

    db.delete(itineraire)
    db.commit()
    return {"ok": True}


# ---------- PRÉFÉRENCES ----------

class PreferencesRequest(BaseModel):
    langue_preferee: str | None = None
    devise_preferee: str | None = None


@router.get("/preferences")
def lire_preferences(user: Utilisateur = Depends(get_current_user)):
    return {"langue_preferee": user.langue_preferee, "devise_preferee": user.devise_preferee}


@router.put("/preferences")
def modifier_preferences(
    request: PreferencesRequest,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    if request.langue_preferee is not None:
        user.langue_preferee = request.langue_preferee
    if request.devise_preferee is not None:
        user.devise_preferee = request.devise_preferee
    db.commit()
    return {"langue_preferee": user.langue_preferee, "devise_preferee": user.devise_preferee}


# ---------- RECOMMANDATIONS ----------

@router.get("/recommandations")
def obtenir_recommandations(
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
):
    favoris_pays = [
        f.nom for f in db.query(Favori).filter(
            Favori.user_id == user.id, Favori.type_destination == "pays"
        ).all()
    ]
    return {"recommandations": recommander_destinations(favoris_pays)}