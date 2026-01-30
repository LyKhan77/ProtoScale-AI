import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { templateCompilerOptions } from '@tresjs/core'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: templateCompilerOptions,
      },
    }),
  ],
  server: {
    port: 5152,
    host: true,
  },
})
