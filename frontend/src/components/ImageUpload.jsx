/**
 * ImageUpload.jsx
 * ----------------
 * Componente que permite:
 *  - Seleccionar/subir una imagen (JPG/PNG)
 *  - Obtener la ubicación del navegador (HTML5 Geolocation API) como respaldo
 *    si la imagen no trae coordenadas GPS en el EXIF
 *  - Permitir ingreso manual de latitud/longitud
 *  - Enviar todo al backend para su procesamiento
 */

import { useState } from "react";
import { detectIncident } from "../services/api";

export default function ImageUpload({ onResult }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [browserLocation, setBrowserLocation] = useState(null);
  const [manualLat, setManualLat] = useState("");
  const [manualLng, setManualLng] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleFileChange(e) {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
  }

  function handleUseBrowserLocation() {
    if (!navigator.geolocation) {
      setError("Tu navegador no soporta geolocalización.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setBrowserLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (err) => setError("No se pudo obtener la ubicación: " + err.message)
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      setError("Selecciona una imagen primero.");
      return;
    }

    // Prioridad de ubicación enviada como respaldo (el backend prioriza EXIF):
    // 1. Ubicación del navegador  2. Ubicación manual  3. Ninguna
    let location = {};
    if (browserLocation) {
      location = { ...browserLocation, source: "browser" };
    } else if (manualLat && manualLng) {
      location = {
        latitude: parseFloat(manualLat),
        longitude: parseFloat(manualLng),
        source: "manual",
      };
    }

    setLoading(true);
    setError(null);
    try {
      const result = await detectIncident(file, location);
      onResult(result);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Ocurrió un error al procesar la imagen."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>1. Subir imagen de la incidencia</h2>

      <input type="file" accept="image/jpeg,image/png" onChange={handleFileChange} />

      {preview && <img className="preview" src={preview} alt="Previsualización" />}

      <h3>2. Ubicación (opcional, se usa si la foto no trae GPS en el EXIF)</h3>
      <div className="location-row">
        <button type="button" onClick={handleUseBrowserLocation}>
          📍 Usar mi ubicación actual
        </button>
        {browserLocation && (
          <span className="badge">
            Lat: {browserLocation.latitude.toFixed(5)}, Lng:{" "}
            {browserLocation.longitude.toFixed(5)}
          </span>
        )}
      </div>

      <div className="location-row">
        <input
          type="number"
          step="any"
          placeholder="Latitud manual"
          value={manualLat}
          onChange={(e) => setManualLat(e.target.value)}
        />
        <input
          type="number"
          step="any"
          placeholder="Longitud manual"
          value={manualLng}
          onChange={(e) => setManualLng(e.target.value)}
        />
      </div>

      {error && <p className="error">{error}</p>}

      <button className="primary" type="submit" disabled={loading}>
        {loading ? "Procesando imagen..." : "Analizar incidencia"}
      </button>
    </form>
  );
}
