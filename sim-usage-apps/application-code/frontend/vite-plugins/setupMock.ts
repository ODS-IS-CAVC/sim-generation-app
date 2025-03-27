import type { ViteDevServer } from 'vite';

export const setupMockPlugin = () => ({
  name: 'mock',
  configureServer(server: ViteDevServer) {
    createMockServer(server.middlewares);
  },
});
