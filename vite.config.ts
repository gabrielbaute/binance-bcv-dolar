import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: "app/ui/static",
    emptyOutDir: false,
    cssCodeSplit: false,
    rollupOptions: {
      input: "app/ui/src/main.ts",
      output: {
        entryFileNames: "js/app.js",
        assetFileNames: (asset) =>
          asset.names.some((name) => name.endsWith(".css"))
            ? "css/app.css"
            : "assets/[name]-[hash][extname]",
      },
    },
  },
});
