import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // This alias must match the one in tsconfig.json
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173, // Default Vite port
    proxy: {
      // Proxy requests from /api to the backend service
      // This should point to the NGINX reverse proxy, which then routes to the correct service
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        // The rewrite is not needed here as NGINX handles the full path
        // In our case, the orders service has a /api/v1/orders prefix, so this is fine.
        // rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
