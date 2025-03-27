import { fileURLToPath, URL } from 'url';

import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import { setupMockPlugin } from './vite-plugins/setupMock';
import viteCompression from 'vite-plugin-compression';

// https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin
import vuetify from 'vite-plugin-vuetify';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const plugins = [
    vue(),
    vueJsx(),
    vuetify({
      autoImport: true,
      styles: { configFile: './src/styles/settings.scss' },
    }),
  ];
  const env = loadEnv(mode, process.cwd() + '/config/env/');

  return {
    base: '/',
    envDir: './config/env/',
    build: {
      emptyOutDir: true,
      outDir: 'dist',
      rollupOptions: {
        output: {
          chunkFileNames: 'assets/[name]-[hash].js',
          assetFileNames: 'assets/[name]-[hash].css',
          entryFileNames: 'assets/[name]-[hash].js',
        },
      },
      //prdとstgの場合はソースマッピングファイルが作成されていません
      sourcemap: mode !== 'prd' && mode !== 'stg',
    },
    //prdとstgの場合は圧縮プラグインを利用します
    plugins:
      mode === 'mock'
        ? [...plugins, setupMockPlugin()]
        : [
            mode === 'prd' || mode === 'stg'
              ? [...plugins, viteCompression()]
              : plugins,
          ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_ENDPOINT_ORIGIN,
          changeOrigin: true,
          configure: (proxy, options) => {
            options.autoRewrite = true;
            options.secure = false;
          },
        },
        '/swagger': {
          target: env.VITE_BACKEND_ENDPOINT_ORIGIN,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
