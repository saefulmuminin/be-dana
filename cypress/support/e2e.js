// ***********************************************************
// This support file is automatically loaded before test files.
// ***********************************************************

// Import commands.js
import './commands'

// Global configuration
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  return false
})

// Before each test
beforeEach(() => {
  // Clear cookies and local storage
  cy.clearCookies()
  cy.clearLocalStorage()
})

// After each test
afterEach(function() {
  // Log test status
  if (this.currentTest.state === 'failed') {
    cy.log(`❌ Test Failed: ${this.currentTest.title}`)
  } else if (this.currentTest.state === 'passed') {
    cy.log(`✅ Test Passed: ${this.currentTest.title}`)
  }
})
