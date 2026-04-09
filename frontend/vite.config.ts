import { defineConfig } from "vite";

// Load environment variables from the repo root .env (one file for the whole project).
export default defineConfig({
  envDir: "..",
});
