"""
auth/database.py

Configuration de la base de données SQLite via SQLAlchemy, et modèles
des tables : utilisateurs, favoris, historique de recherche, itinéraires.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./data/utilisateurs.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe_hash = Column(String, nullable=False)
    langue_preferee = Column(String, default="fr")
    devise_preferee = Column(String, default="EUR")

    favoris = relationship("Favori", back_populates="utilisateur", cascade="all, delete-orphan")
    historique = relationship("RechercheHistorique", back_populates="utilisateur", cascade="all, delete-orphan")
    itineraires = relationship("Itineraire", back_populates="utilisateur", cascade="all, delete-orphan")

class Favori(Base):
    __tablename__ = "favoris"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    type_destination = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    date_ajout = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="favoris")


class RechercheHistorique(Base):
    __tablename__ = "historique_recherches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    terme_recherche = Column(String, nullable=False)
    date_recherche = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="historique")


class Itineraire(Base):
    __tablename__ = "itineraires"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    titre = Column(String, nullable=False)
    contenu_json = Column(Text, nullable=False)  # liste d'étapes sérialisée en JSON
    date_creation = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", back_populates="itineraires")


def get_db():
    """Fournit une session de base de données, fermée automatiquement après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialiser_base():
    """Crée les tables si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)