import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/brain-ui/', // For GitHub Pages deployment
  build: {
    outDir: 'dist',
  },
  server: {
    port: 3000,
  }
})