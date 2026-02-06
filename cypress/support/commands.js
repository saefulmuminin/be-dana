// ***********************************************
// Custom commands for DANA API testing
// ***********************************************

/**
 * Create DANA payment order
 * @param {Object} orderData - Order data (nominal, email, nama_lengkap, etc.)
 * @returns {Cypress.Chainable} Response with orderId and tradeNO
 */
Cypress.Commands.add('createOrder', (orderData = {}) => {
  const defaultData = {
    nominal: Cypress.env('testAmount') || 10000,
    email: Cypress.env('testEmail') || 'test@example.com',
    nama_lengkap: Cypress.env('testName') || 'Test User',
    campaign_id: Cypress.env('testCampaignId') || 1,
    tipe_zakat: 'Zakat Mal',
    doa_muzaki: 'Semoga berkah',
    hamba_allah: false
  }

  const payload = { ...defaultData, ...orderData }

  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/v1/dana/create-order`,
    body: payload,
    headers: {
      'Content-Type': 'application/json'
    },
    failOnStatusCode: false
  }).then((response) => {
    // Save orderId and tradeNO to Cypress env for next tests
    if (response.status === 200 && response.body.status === 'success') {
      Cypress.env('currentOrderId', response.body.data.orderId)
      Cypress.env('currentTradeNO', response.body.data.tradeNO)
    }
    return cy.wrap(response)
  })
})

/**
 * Query payment status
 * @param {String} orderId - Order ID to query
 * @returns {Cypress.Chainable} Response with payment status
 */
Cypress.Commands.add('queryPayment', (orderId) => {
  const orderIdToQuery = orderId || Cypress.env('currentOrderId')

  return cy.request({
    method: 'GET',
    url: `${Cypress.env('apiUrl')}/api/v1/dana/query-payment/${orderIdToQuery}`,
    failOnStatusCode: false
  })
})

/**
 * Cancel payment order
 * @param {String} orderId - Order ID to cancel
 * @param {String} reason - Cancellation reason
 * @returns {Cypress.Chainable} Response
 */
Cypress.Commands.add('cancelOrder', (orderId, reason = 'Test cancellation') => {
  const orderIdToCancel = orderId || Cypress.env('currentOrderId')

  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/v1/dana/cancel-order`,
    body: {
      order_id: orderIdToCancel,
      reason: reason
    },
    headers: {
      'Content-Type': 'application/json'
    },
    failOnStatusCode: false
  })
})

/**
 * Simulate payment finish callback
 * @param {String} orderId - Order ID
 * @param {String} resultCode - Result code (9000, 4000, 6001, etc.)
 * @returns {Cypress.Chainable} Response
 */
Cypress.Commands.add('finishPayment', (orderId, resultCode = '9000') => {
  const orderIdToFinish = orderId || Cypress.env('currentOrderId')

  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/v1/dana/finish-payment`,
    body: {
      orderId: orderIdToFinish,
      resultCode: resultCode,
      resultStatus: resultCode === '9000' ? 'SUCCESS' : 'FAILED'
    },
    headers: {
      'Content-Type': 'application/json'
    },
    failOnStatusCode: false
  })
})

/**
 * Send webhook notification from DANA
 * @param {Object} webhookData - Webhook payload
 * @returns {Cypress.Chainable} Response
 */
Cypress.Commands.add('sendWebhook', (webhookData = {}) => {
  const defaultData = {
    originalPartnerReferenceNo: Cypress.env('currentOrderId'),
    originalReferenceNo: `DANA-REF-${Date.now()}`,
    merchantId: Cypress.env('merchantId'),
    amount: {
      value: '10000.00',
      currency: 'IDR'
    },
    latestTransactionStatus: 'SUCCESS',
    transactionStatusDesc: 'Payment successful'
  }

  const payload = { ...defaultData, ...webhookData }

  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/api/v1/dana/webhook`,
    body: payload,
    headers: {
      'Content-Type': 'application/json',
      'X-SIGNATURE': 'test-signature',
      'X-TIMESTAMP': new Date().toISOString()
    },
    failOnStatusCode: false
  })
})

/**
 * Send SNAP API finish notify
 * @param {Object} notifyData - Notify payload
 * @returns {Cypress.Chainable} Response
 */
Cypress.Commands.add('sendFinishNotify', (notifyData = {}) => {
  const defaultData = {
    originalPartnerReferenceNo: Cypress.env('currentOrderId'),
    originalReferenceNo: `DANA-REF-${Date.now()}`,
    merchantId: Cypress.env('merchantId'),
    amount: {
      value: '10000.00',
      currency: 'IDR'
    },
    latestTransactionStatus: '00', // 00 = Success, 05 = Cancelled
    transactionStatusDesc: 'Payment successful'
  }

  const payload = { ...defaultData, ...notifyData }

  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/v1.0/debit/notify`,
    body: payload,
    headers: {
      'Content-Type': 'application/json',
      'X-SIGNATURE': 'test-signature',
      'X-TIMESTAMP': new Date().toISOString()
    },
    failOnStatusCode: false
  })
})

/**
 * Get user profile (requires auth)
 * @returns {Cypress.Chainable} Response with user profile
 */
Cypress.Commands.add('getUserProfile', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('apiUrl')}/api/v1/user/profile`,
    headers: {
      'Authorization': `Bearer ${Cypress.env('jwtToken')}`
    },
    failOnStatusCode: false
  })
})

/**
 * Health check
 * @returns {Cypress.Chainable} Response
 */
Cypress.Commands.add('healthCheck', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('apiUrl')}/api/v1/auth/health`,
    failOnStatusCode: false
  })
})

/**
 * Validate API response structure
 * @param {Object} response - API response
 * @param {Number} expectedStatus - Expected HTTP status code
 * @param {String} expectedResponseCode - Expected DANA response code
 */
Cypress.Commands.add('validateResponse', (response, expectedStatus, expectedResponseCode = null) => {
  expect(response.status).to.equal(expectedStatus)
  expect(response.body).to.have.property('status')

  if (expectedResponseCode) {
    expect(response.body).to.have.property('responseCode', expectedResponseCode)
  }
})

/**
 * Wait for payment status to change
 * @param {String} orderId - Order ID
 * @param {String} expectedStatus - Expected status (success, failed, pending)
 * @param {Number} maxAttempts - Maximum retry attempts
 * @param {Number} delayMs - Delay between attempts in milliseconds
 */
Cypress.Commands.add('waitForPaymentStatus', (orderId, expectedStatus, maxAttempts = 10, delayMs = 2000) => {
  let attempts = 0

  function checkStatus() {
    return cy.queryPayment(orderId).then((response) => {
      attempts++

      if (response.body.data && response.body.data.status === expectedStatus) {
        cy.log(`✅ Payment status is ${expectedStatus} after ${attempts} attempts`)
        return cy.wrap(response)
      } else if (attempts >= maxAttempts) {
        cy.log(`❌ Payment status did not reach ${expectedStatus} after ${maxAttempts} attempts`)
        return cy.wrap(response)
      } else {
        cy.log(`⏳ Waiting for status ${expectedStatus}... (attempt ${attempts}/${maxAttempts})`)
        cy.wait(delayMs)
        return checkStatus()
      }
    })
  }

  return checkStatus()
})

/**
 * Generate unique test identifier
 * @returns {String} Unique identifier
 */
Cypress.Commands.add('generateTestId', () => {
  return cy.wrap(`TEST-${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}`)
})

/**
 * Log test scenario
 * @param {String} scenario - Scenario name
 * @param {String} description - Scenario description
 */
Cypress.Commands.add('logScenario', (scenario, description) => {
  cy.log('═══════════════════════════════════════')
  cy.log(`📋 Scenario: ${scenario}`)
  cy.log(`📝 Description: ${description}`)
  cy.log('═══════════════════════════════════════')
})
