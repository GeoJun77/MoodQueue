import { defineConfig } from 'vite';

// In development the web app runs on :5173 and forwards /api calls to the
// backend on :8000, so no CORS or URL configuration is needed.
// (Vite compiles JSX natively; no React plugin required.)
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
});
