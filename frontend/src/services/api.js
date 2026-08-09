/**
 * api.js
 * ------
 * Cliente centralizado para consumir la API REST del backend (FastAPI).
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Envía una imagen (y opcionalmente coordenadas) al backend para que
 * ejecute la detección con YOLOv8 y devuelva los resultados.
 *
 * @param {File} file - archivo de imagen (JPG/PNG)
 * @param {{latitude?: number, longitude?: number, source?: string}} location
 */
export async function detectIncident(file, location = {}) {
  const formData = new FormData();
  formData.append("file", file);

  if (location.latitude != null && location.longitude != null) {
    formData.append("latitude", location.latitude);
    formData.append("longitude", location.longitude);
    formData.append("location_source", location.source || "manual");
  }

  const response = await api.post("/api/incidents/detect", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

/** Guarda una incidencia ya detectada en la base de datos. */
export async function saveIncident(payload) {
  const response = await api.post("/api/incidents/", payload);
  return response.data;
}

/** Obtiene el listado de incidencias guardadas (para mostrarlas en el mapa/historial). */
export async function listIncidents() {
  const response = await api.get("/api/incidents/");
  return response.data;
}

export function resolveImageUrl(path) {
  if (!path) return null;
  return path.startsWith("http") ? path : `${API_BASE_URL}${path}`;
}

export default api;
