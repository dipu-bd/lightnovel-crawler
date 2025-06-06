import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react(), tsconfigPaths()],
  build: {
    outDir: '../lncrawl/bots/server/web',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
});
