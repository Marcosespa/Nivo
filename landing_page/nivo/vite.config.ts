import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

const renderExternalHostname = (
  globalThis as {
    process?: {
      env?: Record<string, string | undefined>;
    };
  }
).process?.env?.RENDER_EXTERNAL_HOSTNAME;

const allowedHosts = Array.from(
  new Set(
    [
      'localhost',
      '127.0.0.1',
      'nivo.onrender.com',
      renderExternalHostname,
    ].filter((value): value is string => Boolean(value))
  )
);

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    allowedHosts,
  },
  preview: {
    host: '0.0.0.0',
    allowedHosts,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
});
