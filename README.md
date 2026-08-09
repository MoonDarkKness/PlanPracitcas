# 🏙️ Sistema Inteligente de Detección de Incidencias Urbanas

Prototipo funcional que detecta automáticamente **baches**, **acumulación de basura** y
**luminarias dañadas** en imágenes urbanas usando **YOLOv8**, y geolocaliza cada incidencia
mediante **EXIF GPS**, **HTML5 Geolocation API** o **ingreso manual**.

📄 Ver también: [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md) y [`docs/FLUJO.md`](docs/FLUJO.md)

---

## 📂 Estructura del proyecto

```
incidencias-urbanas/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Punto de entrada FastAPI
│   │   ├── config.py                # Configuración (.env)
│   │   ├── database.py              # Conexión SQLAlchemy
│   │   ├── models.py                # Modelos ORM
│   │   ├── schemas.py               # Esquemas Pydantic
│   │   ├── routers/
│   │   │   └── incidents.py         # Endpoints REST
│   │   ├── services/
│   │   │   ├── detection_service.py # Inferencia YOLOv8 + dibujo de bboxes
│   │   │   ├── exif_service.py      # Extracción de GPS desde EXIF
│   │   │   └── storage_service.py   # Guardado de imágenes en disco
│   │   └── static/
│   │       ├── uploads/             # Imágenes originales subidas
│   │       └── results/             # Imágenes procesadas (con bboxes)
│   ├── train_yolo/
│   │   ├── dataset.yaml             # Config del dataset propio
│   │   ├── train.py                 # Script de entrenamiento
│   │   └── dataset/                 # images/labels (train/val)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx      # Subida de imagen + ubicación
│   │   │   ├── ResultsView.jsx      # Resultados (bboxes, confianza, severidad)
│   │   │   └── MapView.jsx          # Mapa Leaflet
│   │   ├── services/api.js          # Cliente HTTP hacia el backend
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── docs/
    ├── ARQUITECTURA.md
    └── FLUJO.md
```

---

## ⚙️ Requisitos previos

- Python 3.10+
- Node.js 18+ y npm
- (Opcional) GPU NVIDIA + CUDA para acelerar YOLOv8 (funciona también en CPU, solo más lento)

---

## 🚀 Instalación y ejecución

### 1. Backend (FastAPI + YOLOv8)

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# (Edita .env si necesitas cambiar el modelo o la base de datos)

# Ejecutar el servidor de desarrollo
uvicorn app.main:app --reload --port 8000
```

La primera vez que se ejecute, `ultralytics` descargará automáticamente el modelo
base `yolov8n.pt` (pesos preentrenados en COCO, útil solo para probar el pipeline;
**para detectar baches/basura/luminarias reales necesitas entrenar con tu propio dataset**,
ver sección más abajo).

- API disponible en: **http://localhost:8000**
- Documentación interactiva (Swagger): **http://localhost:8000/docs**

### 2. Frontend (React + Vite)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

- Frontend disponible en: **http://localhost:5173**

Si tu backend corre en una URL distinta, crea un archivo `.env` en `frontend/`:

```
VITE_API_URL=http://localhost:8000
```

### 3. Probar el flujo completo

1. Abre `http://localhost:5173`.
2. Sube una foto (idealmente con GPS en el EXIF, tomada con un celular).
3. Opcionalmente, presiona "Usar mi ubicación actual" o ingresa lat/lng manualmente.
4. Haz clic en "Analizar incidencia".
5. Verás la imagen con bounding boxes, el tipo de incidencia, el nivel de confianza y la ubicación en el mapa.
6. Presiona "Guardar incidencia" para persistirla en la base de datos (SQLite por defecto, archivo `backend/incidencias.db`).

---

## 🎯 Entrenar YOLOv8 con tu propio dataset

El modelo base (`yolov8n.pt`) está entrenado en COCO y **no reconoce baches, basura ni
luminarias dañadas** por defecto — solo sirve para validar que el pipeline técnico funciona
end-to-end. Para detección real necesitas hacer fine-tuning:

1. **Recolecta imágenes** representativas (fotos de calles con baches, acumulación de basura,
   postes/luminarias dañadas). Idealmente 150-300 imágenes por clase para un prototipo decente.

2. **Etiqueta las imágenes** en formato YOLO usando una herramienta como:
   - [LabelImg](https://github.com/heartexlabs/labelImg) (offline, simple)
   - [CVAT](https://www.cvat.ai/) (online, colaborativo)
   - [Roboflow](https://roboflow.com/) (online, incluye augmentación y exportación directa a YOLOv8)

   Cada imagen genera un `.txt` con líneas: `<class_id> <x_center> <y_center> <width> <height>`
   (valores normalizados entre 0 y 1). Clases: `0=bache`, `1=basura`, `2=luminaria_danada`.

3. **Organiza el dataset** dentro de `backend/train_yolo/dataset/`:
   ```
   dataset/
     images/train/*.jpg
     images/val/*.jpg
     labels/train/*.txt
     labels/val/*.txt
   ```

4. **Entrena**:
   ```bash
   cd backend/train_yolo
   python train.py
   ```
   El modelo entrenado quedará en `runs/detect/incidencias_urbanas/weights/best.pt`.

5. **Usa el modelo entrenado en el backend**: edita `backend/.env`:
   ```
   YOLO_MODEL_PATH=train_yolo/runs/detect/incidencias_urbanas/weights/best.pt
   ```
   Reinicia el backend (`uvicorn ...`) y las detecciones ahora usarán tu modelo entrenado.

---

## 🗄️ Base de datos

Por defecto usa **SQLite** (archivo local `backend/incidencias.db`, cero configuración).

Para usar **MySQL**, en `backend/.env`:
```
DATABASE_URL=mysql+pymysql://usuario:password@localhost/incidencias_db
```
Y descomenta `pymysql` en `requirements.txt`.

La tabla `incidents` almacena: imagen original, imagen procesada, detecciones (JSON),
latitud/longitud, fuente de la ubicación, severidad y fecha/hora de creación.

---

## 📡 Endpoints principales de la API

| Método | Ruta                        | Descripción                                                        |
|--------|-----------------------------|---------------------------------------------------------------------|
| POST   | `/api/incidents/detect`     | Sube una imagen, ejecuta YOLOv8 y devuelve detecciones + ubicación |
| POST   | `/api/incidents/`           | Guarda una incidencia detectada en la base de datos                |
| GET    | `/api/incidents/`           | Lista todas las incidencias guardadas                              |
| GET    | `/api/incidents/{id}`       | Detalle de una incidencia específica                                |

La API está lista para ser consumida también por una futura app móvil, ya que es
completamente REST/stateless (sin dependencia de sesiones de navegador).

---

## ⚠️ Alcance y limitaciones (prototipo)

- Solo procesa imágenes estáticas (JPG/PNG), no video.
- Máximo 3 clases de incidencias (bache, basura, luminaria dañada).
- El modelo base sin reentrenar no detecta estas clases reales — es indispensable el paso
  de entrenamiento con dataset propio para uso real.
- No incluye autenticación de usuarios ni roles (fácilmente extensible con JWT).
- Pensado para correr localmente / demo; para producción se recomienda contenedores
  (Docker), cola de procesamiento asíncrono y almacenamiento de imágenes en la nube.
