import { useEffect, useState } from "react";
import ImageUpload from "./components/ImageUpload";
import ResultsView from "./components/ResultsView";
import MapView from "./components/MapView";
import { listIncidents } from "./services/api";

export default function App() {
  const [result, setResult] = useState(null);
  const [incidents, setIncidents] = useState([]);

  async function refreshIncidents() {
    try {
      const data = await listIncidents();
      setIncidents(data);
    } catch (e) {
      console.error("No se pudo cargar el historial de incidencias:", e);
    }
  }

  useEffect(() => {
    refreshIncidents();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>🏙️ Detección Inteligente de Incidencias Urbanas</h1>
        <p>Sube una foto de un bache, acumulación de basura o luminaria dañada para analizarla automáticamente.</p>
      </header>

      <main>
        <ImageUpload onResult={setResult} />
        <ResultsView result={result} onSaved={refreshIncidents} />
        <MapView currentResult={result} incidents={incidents} />
      </main>

      <footer>
        <p>Prototipo funcional — Sistema Inteligente de Detección de Incidencias Urbanas</p>
      </footer>
    </div>
  );
}
