import yaml
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent


def main():
    dataset_yaml_path = BASE_DIR / "dataset.yaml"
    dataset_dir = BASE_DIR / "dataset"
    project_path = BASE_DIR / "runs" / "detect"

    # Asegurar que dataset.yaml tenga la ruta absoluta posix correcta para YOLO
    if dataset_yaml_path.exists():
        with open(dataset_yaml_path, "r", encoding="utf-8") as f:
            data_cfg = yaml.safe_load(f)
        data_cfg["path"] = dataset_dir.as_posix()
        with open(dataset_yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(data_cfg, f, default_flow_style=False)

    # Partimos de un modelo YOLOv8 preentrenado (nano: rápido, ideal para prototipo)
    # Alternativas más precisas pero más pesadas: yolov8s.pt, yolov8m.pt
    model_path = BASE_DIR / "yolov8n.pt"
    model = YOLO(str(model_path) if model_path.exists() else "yolov8n.pt")

    model.train(
        data=str(dataset_yaml_path),
        epochs=20,
        imgsz=640,
        batch=16,
        patience=20,       # early stopping si no mejora
        name="incidencias_urbanas",
        project=str(project_path),
        device="cpu",          # usar 0 para GPU; cambia a "cpu" si no tienes GPU
    )

    # Validación final con el set de validación
    metrics = model.val()
    print("Métricas de validación:", metrics)


if __name__ == "__main__":
    main()
