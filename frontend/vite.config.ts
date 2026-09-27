import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { 'react-native': fileURLToPath(new URL('./node_modules/react-native-web/dist/index.js', import.meta.url)) }, dedupe: ['react', 'react-dom'] },
  server: {
    fs: { allow: [fileURLToPath(new URL('..', import.meta.url))] },
    host: true,
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
