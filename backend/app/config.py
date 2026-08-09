"""
config.py
---------
Configuración centralizada de la aplicación.
Lee variables de entorno (.env) usando pydantic-settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Rutas de almacenamiento
    BASE_DIR: Path = Path(__file__).resolve().parent
    UPLOAD_DIR: Path = BASE_DIR / "static" / "uploads"
    RESULTS_DIR: Path = BASE_DIR / "static" / "results"

    # Modelo YOLO
    YOLO_MODEL_PATH: str = str(
        (Path(__file__).resolve().parent.parent / "runs" / "detect" / "incidencias_urbanas-4" / "weights" / "best.pt").resolve()
    ) if (Path(__file__).resolve().parent.parent / "runs" / "detect" / "incidencias_urbanas-4" / "weights" / "best.pt").exists() else "yolov8n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.35

    # Base de datos
    DATABASE_URL: str = "sqlite:///./incidencias.db"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Servidor
    APP_NAME: str = "Sistema Inteligente de Detección de Incidencias Urbanas"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Asegurar que las carpetas de almacenamiento existan
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
