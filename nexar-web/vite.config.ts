import { defineConfig, loadEnv } from 'vite'
import type { ViteDevServer, ResolvedConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

/**
 * Serves /env-config.js dynamically during development so window.__NEXAR_ENV__
 * is populated from .env without a container build (ported from frontend/vite.config.ts).
 */
function runtimeEnvPlugin() {
  let envConfig: Record<string, string> = {}

  return {
    name: 'runtime-env',
    configResolved(config: ResolvedConfig) {
      const env = loadEnv(config.mode, config.root, '')
      envConfig = {
        GOOGLE_CLIENT_ID: env.GOOGLE_CLIENT_ID || '',
        GOOGLE_REDIRECT_URI:
          env.GOOGLE_REDIRECT_URI || 'http://localhost:5173/auth/google/callback',
      }
    },
    configureServer(server: ViteDevServer) {
      server.middlewares.use((req, res, next) => {
        if (req.url === '/env-config.js') {
          res.setHeader('Content-Type', 'application/javascript')
          res.end(`window.__NEXAR_ENV__ = ${JSON.stringify(envConfig, null, 2)};`)
          return
        }
        next()
      })
    },
  }
}

export default defineConfig({
  server: {
    host: '::',
    port: 5173,
  },
  plugins: [
    tailwindcss(),
    react(),
    babel({ presets: [reactCompilerPreset()] }),
    runtimeEnvPlugin(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
