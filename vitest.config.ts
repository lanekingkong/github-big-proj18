import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'dist/'],
      thresholds: {
        branches: 80,
        functions: 85,
        lines: 90,
        statements: 90
      }
    },
    setupFiles: ['./tests/setup.ts']
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@core': resolve(__dirname, './src/core'),
      '@plugins': resolve(__dirname, './src/plugins'),
      '@api': resolve(__dirname, './src/api'),
      '@utils': resolve(__dirname, './src/utils')
    }
  }
});