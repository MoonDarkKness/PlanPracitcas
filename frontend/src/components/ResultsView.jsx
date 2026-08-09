/**
 * ResultsView.jsx
 * ----------------
 * Muestra el resultado de la detección: imagen con bounding boxes,
 * lista de incidencias detectadas con su nivel de confianza y severidad.
 */

import { resolveImageUrl, saveIncident } from "../services/api";
import { useState } from "react";

const SEVERITY_LABELS = {
  alta: { text: "Alta", color: "#e74c3c" },
  media: { text: "Media", color: "#f39c12" },
  baja: { text: "Baja", color: "#27ae60" },
  sin_incidencia: { text: "Sin incidencias detectadas", color: "#7f8c8d" },
};

export default function ResultsView({ result, onSaved }) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!result) return null;

  const { processed_image_url, detections, location, severity } = result;
  const severityInfo = SEVERITY_LABELS[severity] || SEVERITY_LABELS.baja;

  async function handleSave() {
    setSaving(true);
    try {
      const payload = {
        original_filename: result.original_filename,
        processed_image_path: processed_image_url,
        detections,
        latitude: location.latitude,
        longitude: location.longitude,
        location_source: location.source,
        severity,
      };
      const savedIncident = await saveIncident(payload);
      setSaved(true);
      onSaved?.(savedIncident);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <h2>3. Resultados de la detección</h2>

      <img
        className="result-image"
        src={resolveImageUrl(processed_image_url)}
        alt="Resultado con bounding boxes"
      />

      <div className="severity-badge" style={{ backgroundColor: severityInfo.color }}>
        Severidad: {severityInfo.text}
      </div>

      <h3>Incidencias detectadas ({detections.length})</h3>
      {detections.length === 0 && <p>No se detectaron incidencias en esta imagen.</p>}
      <ul className="detections-list">
        {detections.map((d, i) => (
          <li key={i}>
            <strong>{d.class_name}</strong> — confianza:{" "}
            {(d.confidence * 100).toFixed(1)}%
          </li>
        ))}
      </ul>

      <h3>Ubicación</h3>
      {location.latitude != null ? (
        <p>
          Lat: {location.latitude}, Lng: {location.longitude}{" "}
          <span className="badge">fuente: {location.source}</span>
        </p>
      ) : (
        <p>No se pudo determinar la ubicación de esta imagen.</p>
      )}

      <button className="primary" onClick={handleSave} disabled={saving || saved}>
        {saved ? "✅ Guardado" : saving ? "Guardando..." : "Guardar incidencia"}
      </button>
    </div>
  );
}
