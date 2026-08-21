import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests/mcp",
  testMatch: "loopbackBrowserNetwork.spec.ts",
  workers: 1,
  retries: 0,
  use: { browserName: "chromium", trace: "off" },
});
