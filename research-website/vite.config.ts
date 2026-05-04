import { defineConfig } from "vite";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  base: "/nexar/",
  plugins: [TanStackRouterVite(), react(), tailwindcss(), tsConfigPaths()],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
});
