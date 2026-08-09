"""
database.py
-----------
Configuración de la conexión a la base de datos usando SQLAlchemy.
Por defecto usa SQLite (fácil de ejecutar sin instalar nada extra).
Para usar MySQL, cambia DATABASE_URL en el .env, por ejemplo:
DATABASE_URL=mysql+pymysql://usuario:password@localhost/incidencias_db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI para obtener una sesión de base de datos por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
