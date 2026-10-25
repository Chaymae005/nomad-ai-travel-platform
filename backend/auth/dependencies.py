"""
auth/dependencies.py

Dépendance FastAPI qui identifie l'utilisateur courant à partir du
token JWT envoyé dans le header Authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth.database import get_db, Utilisateur
from auth.security import decoder_token

_security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
    db: Session = Depends(get_db),
) -> Utilisateur:
    email = decoder_token(credentials.credentials)
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré.")

    utilisateur = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if utilisateur is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable.")

    return utilisateur