"""
main.py
-------
Punto de entrada de la aplicación FastAPI.

Ejecutar con:
    uvicorn app.main:app --reload --port 8000

Documentación interactiva disponible en:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import incidents

# Crear tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API para detección de incidencias urbanas (baches, basura, luminarias dañadas) "
                "usando visión artificial (YOLOv8) y geolocalización.",
    version="1.0.0",
)

# CORS: permite que el frontend (React) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir imágenes (originales y procesadas) como archivos estáticos
app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "static")), name="static")

# Rutas de la API
app.include_router(incidents.router)


@app.get("/")
def health_check():
    """Endpoint simple para verificar que el servidor está activo."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "docs": "/docs",
    }
