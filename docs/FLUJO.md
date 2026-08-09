# Diagrama de Flujo del Proceso

## Flujo funcional (paso a paso)

```mermaid
flowchart TD
    A[Usuario abre la app web] --> B[Selecciona / sube imagen JPG-PNG]
    B --> C{¿El navegador\nofrece ubicación?}
    C -- Sí --> D[Se captura lat/lng via\nHTML5 Geolocation API]
    C -- No / usuario prefiere manual --> E[Usuario ingresa\nlat/lng manualmente]
    D --> F[POST /api/incidents/detect\nimagen + lat/lng opcional]
    E --> F
    B -- sin usar navegador ni manual --> F

    F --> G[Backend guarda imagen original]
    G --> H{¿Imagen tiene\nEXIF GPS?}
    H -- Sí --> I[Usar coordenadas EXIF\n(prioridad alta)]
    H -- No --> J{¿Se recibió lat/lng\ndesde el frontend?}
    J -- Sí --> K[Usar coordenadas del navegador o manual]
    J -- No --> L[Ubicación desconocida]

    I --> M[Ejecutar modelo YOLOv8\nsobre la imagen]
    K --> M
    L --> M

    M --> N[Dibujar bounding boxes\ny etiquetas de clase/confianza]
    N --> O[Calcular severidad heurística]
    O --> P[Responder al frontend:\nimagen procesada + detecciones + ubicación + severidad]

    P --> Q[Frontend muestra imagen\ncon bounding boxes]
    P --> R[Frontend muestra ubicación\nen mapa Leaflet]
    Q --> S{¿Usuario confirma\nguardar incidencia?}
    R --> S
    S -- Sí --> T[POST /api/incidents/\nGuardar en base de datos]
    T --> U[Incidencia aparece en\nhistorial del mapa]
    S -- No --> V[Fin del flujo\n(no se persiste)]
```

## Descripción textual (alternativa sin Mermaid)

1. **Captura**: el usuario sube una imagen JPG/PNG desde el navegador.
2. **Ubicación (paralelo a la captura)**:
   - El frontend intenta obtener la ubicación actual vía `navigator.geolocation` (HTML5 Geolocation API).
   - Si el usuario prefiere, puede ingresar latitud/longitud manualmente.
3. **Envío**: la imagen (y la ubicación de respaldo, si existe) se envían al backend vía `multipart/form-data` al endpoint `POST /api/incidents/detect`.
4. **Resolución de ubicación en backend** (orden de prioridad):
   1. Metadatos EXIF de la imagen (más confiables).
   2. Ubicación enviada por el navegador.
   3. Ubicación manual.
   4. Ninguna (se marca como "desconocida").
5. **Inferencia con YOLOv8**: el modelo detecta baches, basura y luminarias dañadas, devolviendo clase, confianza y bounding box por cada objeto.
6. **Post-procesamiento**: se dibujan los bounding boxes sobre la imagen (OpenCV) y se calcula una severidad heurística según el tipo de incidencia detectada.
7. **Respuesta al frontend**: JSON con la URL de la imagen procesada, lista de detecciones, ubicación resuelta y severidad.
8. **Visualización**: el frontend muestra la imagen anotada, la lista de incidencias y un mapa (Leaflet) con el marcador correspondiente.
9. **Persistencia (opcional)**: si el usuario confirma, se guarda la incidencia (imagen, detecciones, ubicación, fecha) en la base de datos, y pasa a formar parte del historial visible en el mapa.
