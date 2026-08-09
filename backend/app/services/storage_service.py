"""
storage_service.py
-------------------
Maneja el guardado físico de las imágenes subidas y procesadas en disco.
"""

import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from app.config import settings


class StorageService:

    @staticmethod
    def save_upload(file: UploadFile) -> Path:
        """Guarda el archivo subido por el usuario con un nombre único."""
        extension = Path(file.filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{extension}"
        destination = settings.UPLOAD_DIR / unique_name

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return destination

    @staticmethod
    def build_result_path(original_path: Path) -> Path:
        """Genera la ruta de salida para la imagen ya procesada (con bounding boxes)."""
        result_name = f"result_{original_path.name}"
        return settings.RESULTS_DIR / result_name
