"""
auth/security.py

Hash des mots de passe (bcrypt) et gestion des tokens JWT.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt, JWTError
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set. Copy .env.example to .env and set it.")
ALGORITHM = "HS256"
DUREE_TOKEN_MINUTES = 60 * 24 * 7  # 7 jours

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return _pwd_context.hash(mot_de_passe)


def verifier_mot_de_passe(mot_de_passe: str, mot_de_passe_hash: str) -> bool:
    return _pwd_context.verify(mot_de_passe, mot_de_passe_hash)


def creer_token(email: str, nom: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=DUREE_TOKEN_MINUTES)
    payload = {"sub": email, "nom": nom, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decoder_token(token: str) -> str | None:
    """Retourne l'email contenu dans le token, ou None si invalide/expiré."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None