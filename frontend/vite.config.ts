import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { 'react-native': fileURLToPath(new URL('./node_modules/react-native-web/dist/index.js', import.meta.url)) }, dedupe: ['react', 'react-dom'] },
  build: { rollupOptions: { input: { main: fileURLToPath(new URL('./index.html', import.meta.url)), screen: fileURLToPath(new URL('./screen-preview.html', import.meta.url)) } } },
  server: {
    fs: { allow: [fileURLToPath(new URL('..', import.meta.url))] },
    host: true,
    port: 5173,
  },
})
