# Arquitectura del Sistema

## 1. Visión general

El sistema sigue una arquitectura **cliente-servidor desacoplada**, en tres capas lógicas:

```
┌─────────────────────┐        HTTP/REST (JSON, multipart)      ┌──────────────────────────┐
│      FRONTEND        │ ───────────────────────────────────▶  │         BACKEND            │
│  React + Leaflet     │ ◀───────────────────────────────────  │  FastAPI + YOLOv8 + OpenCV │
│  (Geolocation API)   │                                        │  + SQLAlchemy               │
└─────────────────────┘                                        └───────────┬──────────────┘
                                                                             │
                                                                             ▼
                                                                  ┌──────────────────┐
                                                                  │  Base de datos     │
                                                                  │  SQLite / MySQL    │
                                                                  └──────────────────┘
```

## 2. Capas del backend

El backend está organizado siguiendo separación de responsabilidades:

- **`routers/`** — Capa de presentación (endpoints HTTP). Solo valida entradas/salidas y orquesta llamadas a los servicios.
- **`services/`** — Capa de lógica de negocio:
  - `detection_service.py`: carga el modelo YOLOv8 y ejecuta la inferencia.
  - `exif_service.py`: extrae coordenadas GPS de metadatos EXIF.
  - `storage_service.py`: gestiona el guardado físico de imágenes.
- **`models.py`** — Capa de persistencia (ORM SQLAlchemy).
- **`schemas.py`** — Contratos de datos (Pydantic) para requests/responses.
- **`config.py`** — Configuración centralizada vía variables de entorno.

Esta separación permite, por ejemplo, cambiar el motor de detección (YOLOv8 → otro modelo) sin tocar los endpoints, o cambiar SQLite por MySQL solo modificando `DATABASE_URL`.

## 3. Flujo de datos (resumen)

1. El usuario sube una imagen desde el frontend React.
2. El frontend intenta obtener la ubicación del navegador (HTML5 Geolocation API) como respaldo.
3. La imagen (y opcionalmente lat/lng) se envían al endpoint `POST /api/incidents/detect`.
4. El backend:
   a. Guarda la imagen original.
   b. Intenta leer coordenadas GPS del EXIF de la imagen (prioridad más alta, por ser el dato más preciso).
   c. Si no hay EXIF, usa la ubicación enviada por el frontend (navegador o manual).
   d. Ejecuta el modelo YOLOv8 sobre la imagen y dibuja bounding boxes.
   e. Calcula una severidad heurística según el tipo de incidencia detectada.
5. El backend responde con: imagen procesada (URL), detecciones, ubicación resuelta y severidad.
6. El frontend muestra la imagen con bounding boxes, la lista de detecciones y el mapa (Leaflet).
7. Opcionalmente, el usuario confirma y el frontend llama a `POST /api/incidents/` para persistir la incidencia en base de datos.
8. El historial de incidencias guardadas se consulta vía `GET /api/incidents/` y se pinta como marcadores adicionales en el mapa.

## 4. Por qué estas decisiones técnicas

- **FastAPI**: tipado con Pydantic, generación automática de documentación (`/docs`), rendimiento async, ideal para prototipos que luego escalan.
- **YOLOv8 (Ultralytics)**: modelo de detección de objetos de última generación, con API de alto nivel muy simple (`model.predict(...)`), fácil de reentrenar con dataset propio.
- **SQLite por defecto**: cero configuración para correr el prototipo localmente; migrar a MySQL solo requiere cambiar `DATABASE_URL` y agregar `pymysql`.
- **React + Leaflet**: Leaflet es open-source y no requiere API key (a diferencia de Google Maps), ideal para un prototipo municipal sin costos de licenciamiento.
- **EXIF como fuente primaria de ubicación**: es el dato más confiable (viene de la cámara/GPS del dispositivo en el momento exacto de la foto). El navegador o el ingreso manual son *fallbacks* razonables cuando la imagen no trae esos metadatos (común en capturas de pantalla, imágenes editadas o cámaras sin GPS).

## 5. Extensibilidad futura

- La API ya está lista para ser consumida por una futura app móvil (endpoints REST estándar, sin dependencias de sesión/cookies).
- Se puede añadir autenticación (JWT) para diferenciar operadores municipales.
- El campo `severity` usa reglas heurísticas simples; se puede sustituir por un modelo de clasificación adicional.
- Para producción real se recomendaría: cola de procesamiento (Celery/RQ) para no bloquear el request HTTP durante la inferencia, almacenamiento de imágenes en un bucket (S3/GCS) en vez de disco local, y un modelo YOLOv8 entrenado con dataset real y validado por el equipo técnico municipal.
