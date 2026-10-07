import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true, // 允许通过局域网 IP 访问，如 http://10.11.3.60:5173/
    proxy: {
      '/api/chart-ai-holographic': {
        target: 'http://127.0.0.1:8787',
        changeOrigin: true,
        timeout: 300_000,
        proxyTimeout: 300_000,
      },
      '/api/divination-ai': {
        target: 'http://127.0.0.1:8787',
        changeOrigin: true,
        timeout: 300_000,
        proxyTimeout: 300_000,
      },
    },
  },
});
