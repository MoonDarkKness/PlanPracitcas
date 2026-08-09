"""
models.py
---------
Modelos ORM (SQLAlchemy) que representan las tablas de la base de datos.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Incident(Base):
    """
    Representa una incidencia urbana detectada y almacenada:
    imagen procesada, tipo de incidencia, ubicación y metadatos.
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    # Archivos
    original_filename = Column(String, nullable=False)
    processed_image_path = Column(String, nullable=False)  # imagen con bounding boxes

    # Detecciones (guardadas como JSON: lista de {class, confidence, bbox})
    detections = Column(JSON, nullable=False)

    # Ubicación
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_source = Column(String, nullable=True)  # "exif" | "browser" | "manual"

    # Severidad estimada (opcional)
    severity = Column(String, nullable=True)  # "baja" | "media" | "alta"

    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
