import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // === YENİ VE ÖNEMLİ OLAN KISIM BURASI ===
  server: {
    proxy: {
      // '/api' ile başlayan tüm HTTP isteklerini Django sunucusuna yönlendir
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // '/ws' ile başlayan tüm WebSocket isteklerini de Django'ya (Daphne'ye) yönlendir
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      }
    }
  }
})