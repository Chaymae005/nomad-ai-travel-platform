"""
auth/routes.py

Routes d'inscription et de connexion.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from auth.database import get_db, Utilisateur
from auth.security import hasher_mot_de_passe, verifier_mot_de_passe, creer_token

router = APIRouter(prefix="/auth", tags=["auth"])


class InscriptionRequest(BaseModel):
    nom: str
    email: EmailStr
    mot_de_passe: str


class ConnexionRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str



@router.post("/register")
def register(request: InscriptionRequest, db: Session = Depends(get_db)):
    utilisateur_existant = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()
    if utilisateur_existant:
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email.")

    if len(request.mot_de_passe) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 6 caractères.")

    nouvel_utilisateur = Utilisateur(
        nom=request.nom,
        email=request.email,
        mot_de_passe_hash=hasher_mot_de_passe(request.mot_de_passe),
    )
    db.add(nouvel_utilisateur)
    db.commit()

    token = creer_token(request.email, request.nom)
    return {"token": token, "email": request.email, "nom": request.nom}


@router.post("/login")
def login(request: ConnexionRequest, db: Session = Depends(get_db)):
    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == request.email).first()

    if not utilisateur or not verifier_mot_de_passe(request.mot_de_passe, utilisateur.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")

    token = creer_token(request.email, utilisateur.nom)
    return {"token": token, "email": request.email, "nom": utilisateur.nom}