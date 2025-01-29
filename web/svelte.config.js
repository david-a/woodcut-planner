import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://svelte.dev/docs/kit/integrations
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    // adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
    // If your environment is not supported, or you settled on a specific environment, switch out the adapter.
    // See https://svelte.dev/docs/kit/adapters for more information about adapters.
    adapter: adapter({
      // You can specify node adapter options here if needed
      out: "build",
    }),
    alias: {
      $lib: "src/lib",
      $components: "src/lib/components",
    },
    files: {
      assets: "static",
      lib: "src/lib",
      routes: "src/routes",
      appTemplate: "src/app.html",
    },
    env: {
      dir: process.cwd(),
    },
  },
};

export default config;
