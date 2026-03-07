import { defineConfig, loadEnv } from "vite";
import type { ViteDevServer, ResolvedConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

/**
 * Vite plugin that serves /env-config.js dynamically during development.
 * Reads GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI from .env files so that
 * window.__NEXAR_ENV__ is populated without a Docker build.
 */
function runtimeEnvPlugin() {
  let envConfig: Record<string, string> = {};

  return {
    name: "runtime-env",
    configResolved(config: ResolvedConfig) {
      const env = loadEnv(config.mode, config.root, "");
      envConfig = {
        GOOGLE_CLIENT_ID: env.GOOGLE_CLIENT_ID || "",
        GOOGLE_REDIRECT_URI:
          env.GOOGLE_REDIRECT_URI ||
          "http://localhost:5173/auth/google/callback",
      };
    },
    configureServer(server: ViteDevServer) {
      server.middlewares.use((req, res, next) => {
        if (req.url === "/env-config.js") {
          res.setHeader("Content-Type", "application/javascript");
          res.end(
            `window.__NEXAR_ENV__ = ${JSON.stringify(envConfig, null, 2)};`,
          );
          return;
        }
        next();
      });
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 5173,
  },
  plugins: [
    react(),
    runtimeEnvPlugin(),
    mode === "development" && componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
