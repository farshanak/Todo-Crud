/// <reference types="vitest" />
import { defineConfig } from "vite";

export default defineConfig({
  envDir: "..",
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    coverage: {
      provider: "v8",
      include: ["src/api.ts"],
      thresholds: {
        lines: 90,
        statements: 90,
        functions: 90,
        branches: 90,
      },
    },
  },
});
