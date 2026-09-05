import { readFileSync } from "node:fs";
import { extname, join } from "node:path";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const LANDING_DIR = join(__dirname, "..", "landing-page");
const MIME: Record<string, string> = { ".html": "text/html", ".svg": "image/svg+xml" };

// Serves the standalone landing-page/ folder at /landing — not part of the
// React app/build, just a static file drop for the marketing page.
function landingPage(): Plugin {
  return {
    name: "landing-page",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!req.url || !req.url.replace(/\/$/, "").match(/^\/landing(\/.*)?$/)) return next();
        const rest = req.url.replace(/^\/landing\/?/, "") || "index.html";
        const path = rest === "favicon.svg" ? join(LANDING_DIR, "favicon.svg") : join(LANDING_DIR, "index.html");
        try {
          res.setHeader("Content-Type", MIME[extname(path)] ?? "application/octet-stream");
          res.end(readFileSync(path));
        } catch {
          next();
        }
      });
    },
  };
}

// Dev server proxies /api to the backend so the frontend needs no CORS config
// and VITE_API_BASE_URL can stay empty in local dev.
export default defineConfig({
  plugins: [react(), landingPage()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY ?? "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
