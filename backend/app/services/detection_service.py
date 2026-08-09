import cv2
from ultralytics import YOLO
from pathlib import Path
from app.config import settings

# Mapeo severidad simple basado en el tipo de incidencia y tamaño del bbox.
# Esto es un criterio heurístico de ejemplo, ajustable según reglas del municipio.
SEVERITY_RULES = {
    "bache": "alta",
    "baches": "alta",
    "basura": "media",
    "posteCaido": "media",
    "luminaria_danada": "media",
}

# Colores BGR para dibujar cada clase
CLASS_COLORS = {
    "bache": (0, 0, 255),
    "baches": (0, 0, 255),
    "basura": (0, 165, 255),
    "posteCaido": (255, 0, 0),
    "luminaria_danada": (255, 0, 0)
}
class DetectionService:
    """Encapsula la carga del modelo y la inferencia sobre imágenes."""

    _model = None  # Singleton: el modelo se carga una sola vez en memoria

    @classmethod
    def get_model(cls) -> YOLO:
        if cls._model is None:
            cls._model = YOLO(settings.YOLO_MODEL_PATH)
        return cls._model

    @classmethod
    def detect(cls, image_path: Path, output_path: Path) -> list[dict]:
        
        model = cls.get_model()
        results = model.predict(
            source=str(image_path),
            conf=settings.YOLO_CONFIDENCE_THRESHOLD,
            verbose=False,
        )

        image = cv2.imread(str(image_path))
        detections = []

        result = results[0]
        names = result.names  # dict {id: nombre_clase}

        for box in result.boxes:
            cls_id = int(box.cls[0])
            class_name = names.get(cls_id, str(cls_id))
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]

            detections.append({
                "class_name": class_name,
                "confidence": round(confidence, 4),
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
            })

            # Dibujar bounding box + etiqueta
            color = CLASS_COLORS.get(class_name, (0, 255, 0))
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            label = f"{class_name} {confidence:.2f}"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(image, (int(x1), int(y1) - th - 8), (int(x1) + tw + 4, int(y1)), color, -1)
            cv2.putText(image, label, (int(x1) + 2, int(y1) - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imwrite(str(output_path), image)
        return detections

    @staticmethod
    def estimate_severity(detections: list[dict]) -> str:
        """
        Estima la severidad global de la incidencia detectada en la imagen.
        Regla simple: toma la severidad más alta entre todas las detecciones.
        """
        if not detections:
            return "sin_incidencia"

        order = {"baja": 0, "media": 1, "alta": 2}
        max_severity = "baja"
        for d in detections:
            sev = SEVERITY_RULES.get(d["class_name"], "baja")
            if order[sev] > order[max_severity]:
                max_severity = sev
        return max_severity
