/// <reference types="vitest/config" />
// Vite dev server and build settings. /api calls are proxied to the FastAPI backend on port 8000.
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'node',
  },
})
