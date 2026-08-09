/**
 * MapView.jsx
 * -----------
 * Muestra un mapa (Leaflet) con marcadores para:
 *  - La incidencia recién detectada (si tiene ubicación)
 *  - El historial de incidencias guardadas en la base de datos
 */

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

// Fix del ícono por defecto de Leaflet en bundlers como Vite
import icon from "leaflet/dist/images/marker-icon.png";
import iconShadow from "leaflet/dist/images/marker-shadow.png";

const defaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = defaultIcon;

const DEFAULT_CENTER = [-9.19, -75.0152]; // Centro aproximado de Perú, como fallback

export default function MapView({ currentResult, incidents = [] }) {
  const currentLocation =
    currentResult?.location?.latitude != null
      ? [currentResult.location.latitude, currentResult.location.longitude]
      : null;

  const center = currentLocation || DEFAULT_CENTER;

  return (
    <div className="card">
      <h2>4. Mapa de incidencias</h2>
      <MapContainer center={center} zoom={currentLocation ? 15 : 6} style={{ height: "400px", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Marcador de la incidencia recién analizada */}
        {currentLocation && (
          <Marker position={currentLocation}>
            <Popup>
              Incidencia recién detectada
              <br />
              Severidad: {currentResult.severity}
            </Popup>
          </Marker>
        )}

        {/* Historial de incidencias guardadas */}
        {incidents
          .filter((inc) => inc.latitude != null && inc.longitude != null)
          .map((inc) => (
            <Marker key={inc.id} position={[inc.latitude, inc.longitude]}>
              <Popup>
                <strong>Incidencia #{inc.id}</strong>
                <br />
                Severidad: {inc.severity}
                <br />
                Fecha: {new Date(inc.created_at).toLocaleString()}
              </Popup>
            </Marker>
          ))}
      </MapContainer>
    </div>
  );
}
