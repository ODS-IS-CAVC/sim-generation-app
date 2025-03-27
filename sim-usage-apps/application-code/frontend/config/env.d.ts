/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_BACKEND_ENDPOINT_ORIGIN: string;
  readonly VITE_API_PREFIX: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
