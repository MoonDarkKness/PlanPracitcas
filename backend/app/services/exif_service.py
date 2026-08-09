"""
exif_service.py
----------------
Extrae coordenadas GPS (latitud/longitud) desde los metadatos EXIF
de una imagen, si es que el dispositivo/cámara los guardó al tomar la foto.

Usa Pillow para leer los tags EXIF estándar.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from typing import Optional, Tuple


class ExifService:

    @staticmethod
    def _get_exif_data(image_path: Path) -> dict:
        """Devuelve un diccionario con los tags EXIF legibles de la imagen."""
        image = Image.open(image_path)
        exif_raw = image._getexif()
        if not exif_raw:
            return {}

        exif_data = {}
        for tag_id, value in exif_raw.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "GPSInfo":
                gps_data = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag_name] = gps_value
                exif_data["GPSInfo"] = gps_data
            else:
                exif_data[tag_name] = value
        return exif_data

    @staticmethod
    def _convert_to_degrees(value) -> float:
        """Convierte coordenadas EXIF (grados, minutos, segundos) a formato decimal."""
        d, m, s = value
        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)

    @classmethod
    def get_gps_coordinates(cls, image_path: Path) -> Optional[Tuple[float, float]]:
        """
        Intenta obtener (latitud, longitud) desde el EXIF de la imagen.
        Retorna None si la imagen no tiene metadatos GPS.
        """
        try:
            exif_data = cls._get_exif_data(image_path)
            gps_info = exif_data.get("GPSInfo")
            if not gps_info:
                return None

            lat = cls._convert_to_degrees(gps_info["GPSLatitude"])
            if gps_info.get("GPSLatitudeRef") != "N":
                lat = -lat

            lon = cls._convert_to_degrees(gps_info["GPSLongitude"])
            if gps_info.get("GPSLongitudeRef") != "E":
                lon = -lon

            return round(lat, 6), round(lon, 6)
        except (AttributeError, KeyError, TypeError, ZeroDivisionError):
            # La imagen no tiene EXIF, o no incluye datos GPS válidos
            return None
