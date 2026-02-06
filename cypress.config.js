const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'https://be-dana.vercel.app',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
    video: true,
    screenshot: true,
    viewportWidth: 1280,
    viewportHeight: 720,

    // Test retries
    retries: {
      runMode: 2,
      openMode: 0
    },

    // Timeouts
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,

    // Environment variables
    env: {
      // API URLs
      apiUrl: 'https://be-dana.vercel.app',
      danaApiUrl: 'https://api.sandbox.dana.id',

      // Merchant Credentials
      merchantId: '216620010022044847375',
      clientId: '2026020413531650671653',
      channelId: '95221',

      // JWT Token (update if expired)
      jwtToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJtdXpha2lfaWQiOjEsInR5cGUiOiJ1c2VyIiwiZXhwIjoxNzcwMjc1MTMyfQ.oCUKWxgBl_fPy41YPGbboT1L5rcFnXjPMT0voOKOo8o',

      // Test data
      testEmail: 'test.uat@example.com',
      testName: 'UAT Test User',
      testAmount: 10000,
      testCampaignId: 1
    },

    setupNodeEvents(on, config) {
      // implement node event listeners here

      // Allow switching environments
      const environment = config.env.ENVIRONMENT || 'production'

      if (environment === 'local') {
        config.baseUrl = 'http://127.0.0.1:5000'
        config.env.apiUrl = 'http://127.0.0.1:5000'
      }

      return config
    },
  },

  // Reporter config for mochawesome
  reporter: 'mochawesome',
  reporterOptions: {
    reportDir: 'cypress/reports',
    overwrite: false,
    html: true,
    json: true,
    timestamp: 'mmddyyyy_HHMMss'
  }
})
