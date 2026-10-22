import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Where the backend lives during development.
// - Local without Docker: http://localhost:8000
// - Inside Docker Compose:  http://backend:8000  (set via env in docker-compose.yml)
const apiTarget = process.env.VITE_API_TARGET ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so Docker/Codespaces can reach it
    port: 5173,
    allowedHosts: true, // needed for Codespaces' *.app.github.dev URLs
    proxy: {
      // The browser calls /api/... on the SAME origin -> no CORS problems.
      "/api": { target: apiTarget, changeOrigin: true },
    },
  },
});
