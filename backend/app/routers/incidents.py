from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.config import settings
from app.services.storage_service import StorageService
from app.services.detection_service import DetectionService
from app.services.exif_service import ExifService
from app import models, schemas

router = APIRouter(prefix="/api/incidents", tags=["Incidencias"])


@router.post("/detect", response_model=schemas.DetectionResponse)
async def detect_incident(
    file: UploadFile = File(..., description="Imagen JPG/PNG a analizar"),
    latitude: Optional[float] = Form(None, description="Latitud manual (opcional, del navegador o ingreso manual)"),
    longitude: Optional[float] = Form(None, description="Longitud manual (opcional)"),
    location_source: Optional[str] = Form(None, description="'browser' o 'manual' si latitude/longitude se envían"),
):
    
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Formato no soportado. Usa JPG o PNG.")

    # 1. Guardar imagen original
    original_path = StorageService.save_upload(file)

    # 2. Ubicación: EXIF primero, luego lo que envíe el frontend
    exif_coords = ExifService.get_gps_coordinates(original_path)
    if exif_coords:
        lat, lon = exif_coords
        source = "exif"
    elif latitude is not None and longitude is not None:
        lat, lon = latitude, longitude
        source = location_source or "manual"
    else:
        lat, lon = None, None
        source = "none"

    # 3. Detección con YOLOv8
    result_path = StorageService.build_result_path(original_path)
    detections = DetectionService.detect(original_path, result_path)
    severity = DetectionService.estimate_severity(detections)

    # 4. Construir respuesta
    processed_image_url = f"/static/results/{result_path.name}"

    return schemas.DetectionResponse(
        original_filename=file.filename,
        processed_image_url=processed_image_url,
        detections=detections,
        location=schemas.LocationInfo(latitude=lat, longitude=lon, source=source),
        severity=severity,
    )


@router.post("/", response_model=schemas.IncidentOut)
def save_incident(payload: schemas.IncidentCreate, db: Session = Depends(get_db)):
    """Guarda en base de datos una incidencia ya detectada (confirmada por el usuario)."""
    incident = models.Incident(
        original_filename=payload.original_filename,
        processed_image_path=payload.processed_image_path,
        detections=[d.model_dump() for d in payload.detections],
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_source=payload.location_source,
        severity=payload.severity,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    """Lista todas las incidencias guardadas (para mostrarlas en el mapa/historial)."""
    return db.query(models.Incident).order_by(models.Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=schemas.IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incidencia no encontrada")
    return incident
