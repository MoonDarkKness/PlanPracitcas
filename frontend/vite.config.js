import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Configuración de Vite para GitHub Pages
export default defineConfig({
  plugins: [react()],

  base: "/PlanPracticas/",

  server: {
    port: 5173,
  },
});
