"""
schemas.py
----------
Esquemas Pydantic usados para validar entradas y formatear salidas de la API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Detection(BaseModel):
    """Una detección individual devuelta por el modelo YOLO."""
    class_name: str = Field(..., description="Tipo de incidencia: bache, basura, luminaria_danada")
    confidence: float = Field(..., ge=0, le=1)
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2] en píxeles")


class LocationInfo(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = Field(None, description="exif | browser | manual | none")


class DetectionResponse(BaseModel):
    """Respuesta del endpoint de procesamiento de imagen."""
    original_filename: str
    processed_image_url: str
    detections: List[Detection]
    location: LocationInfo
    severity: Optional[str] = None


class IncidentCreate(BaseModel):
    """Payload para guardar manualmente una incidencia (si el usuario confirma)."""
    original_filename: str
    processed_image_path: str
    detections: List[Detection]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_source: Optional[str] = None
    severity: Optional[str] = None


class IncidentOut(BaseModel):
    id: int
    original_filename: str
    processed_image_path: str
    detections: List[Detection]
    latitude: Optional[float]
    longitude: Optional[float]
    location_source: Optional[str]
    severity: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
