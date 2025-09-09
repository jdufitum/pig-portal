import type { PlaywrightTestConfig } from '@playwright/test'

const config: PlaywrightTestConfig = {
  testDir: './tests/e2e',
  timeout: 60_000,
  globalSetup: './tests/e2e/global-setup.ts',
  use: {
    baseURL: 'http://localhost',
    browserName: 'chromium',
    headless: true,
  },
}

export default config

