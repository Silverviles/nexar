/// <reference types="vite/client" />

interface NexarEnv {
  GOOGLE_CLIENT_ID: string;
  GOOGLE_REDIRECT_URI: string;
}

declare global {
  interface Window {
    __NEXAR_ENV__?: NexarEnv;
  }
}

export {};
