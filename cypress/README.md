# Cypress UAT Testing - DANA Payment API

Automated UAT (User Acceptance Testing) suite untuk DANA Payment Integration menggunakan Cypress.

## 📦 Test Coverage

### 1. Direct Debit Payment (7 Scenarios)
**File:** `cypress/e2e/uat/direct-debit-payment.cy.js`

- ✅ Scenario 1: Successfully requests Create Order (2005400)
- ✅ Scenario 2: Missing or invalid mandatory field (4005402)
- ✅ Scenario 3: General Error (5005400)
- ✅ Scenario 4: Transaction not permitted (4035415)
- ✅ Scenario 5: Invalid Merchant (4045408)
- ✅ Scenario 6: Inconsistent Request (4045418)
- ✅ Scenario 7: Internal Server Error (5005401)

### 2. Payment Finish Notify (3 Scenarios)
**File:** `cypress/e2e/uat/payment-finish-notify.cy.js`

- ✅ Scenario 1: Transaction Success Notify (00 = Success)
- ✅ Scenario 2: Internal Server Error Response
- ✅ Scenario 3: Transaction Closed/Expired (05 = Cancelled)
- ✅ Additional: Webhook Security & Validation

**Total: 10+ test scenarios + additional security tests**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

Ini akan install:
- `cypress` - Test framework
- `mochawesome` - Report generator
- Related dependencies

### 2. Run Tests

**Interactive Mode (Recommended for development):**
```bash
npm run test:open
```
- Opens Cypress Test Runner GUI
- Select test files to run
- Watch tests execute in real-time
- Easy debugging

**Headless Mode (CI/CD):**
```bash
npm test
# or
npm run test:uat
```
- Runs all UAT tests
- No GUI (headless)
- Generates video recordings
- Perfect for automated testing

**Run Specific Test Suite:**
```bash
# Direct Debit Payment tests only
npm run test:payment

# Payment Finish Notify tests only
npm run test:webhook
```

**Generate HTML Report:**
```bash
npm run test:report
```
- Runs tests with mochawesome reporter
- Generates HTML report in `cypress/reports/`
- Beautiful, shareable test results

## 📁 Project Structure

```
cypress/
├── e2e/
│   └── uat/
│       ├── direct-debit-payment.cy.js    # 7 payment scenarios
│       └── payment-finish-notify.cy.js   # 3 webhook scenarios
├── support/
│   ├── e2e.js                             # Global config
│   └── commands.js                        # Custom commands
├── videos/                                # Test recordings
├── screenshots/                           # Failure screenshots
└── reports/                               # Test reports

cypress.config.js                          # Cypress configuration
```

## 🔧 Configuration

### Environment Variables

Edit `cypress.config.js` atau set via command line:

```javascript
// Production (default)
baseUrl: 'https://be-dana.vercel.app'
apiUrl: 'https://be-dana.vercel.app'

// Local development
ENVIRONMENT=local npm run test:open
// Uses: http://127.0.0.1:5000
```

### Merchant Credentials

Pre-configured di `cypress.config.js`:
```javascript
env: {
  merchantId: '216620010022044847375',
  clientId: '2026020413531650671653',
  channelId: '95221',
  jwtToken: 'your_jwt_token_here'
}
```

Update JWT token jika expired.

## 🧪 Custom Commands

### Payment Commands

```javascript
// Create order
cy.createOrder({
  nominal: 10000,
  email: 'test@example.com',
  nama_lengkap: 'Test User'
})

// Query payment
cy.queryPayment(orderId)

// Cancel order
cy.cancelOrder(orderId, 'Reason')

// Finish payment
cy.finishPayment(orderId, '9000') // 9000 = success

// Send webhook notification
cy.sendWebhook({
  originalPartnerReferenceNo: orderId,
  latestTransactionStatus: 'SUCCESS'
})

// Send SNAP API finish notify
cy.sendFinishNotify({
  originalPartnerReferenceNo: orderId,
  latestTransactionStatus: '00' // 00 = success
})
```

### Utility Commands

```javascript
// Health check
cy.healthCheck()

// Get user profile (requires auth)
cy.getUserProfile()

// Wait for payment status
cy.waitForPaymentStatus(orderId, 'success', maxAttempts, delayMs)

// Generate unique test ID
cy.generateTestId()

// Log test scenario
cy.logScenario('Scenario Name', 'Description')

// Validate response
cy.validateResponse(response, expectedStatus, expectedCode)
```

## 📊 Test Reports

### Viewing Reports

After running tests with `npm run test:report`:

```bash
# Open HTML report
open cypress/reports/mochawesome.html
```

Report includes:
- ✅ Pass/Fail status for each test
- ⏱️ Execution time
- 📸 Screenshots (for failures)
- 📹 Video recordings
- 📝 Detailed logs

### Continuous Integration

For CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Cypress Tests
  run: npm run test:uat

- name: Upload Test Results
  uses: actions/upload-artifact@v2
  with:
    name: cypress-results
    path: |
      cypress/videos
      cypress/screenshots
      cypress/reports
```

## 🎯 UAT Testing Workflow

### Step 1: Run All Tests

```bash
npm run test:uat
```

### Step 2: Review Results

Check console output:
```
  UAT: Direct Debit Payment - Cashier Pay
    Scenario 1: Successfully requests Create Order
      ✓ Should create order successfully (523ms)
      ✓ Should be able to query the created order (234ms)
    Scenario 2: Missing or invalid format on mandatory field
      ✓ Should return error when email is missing (145ms)
      ...

  10 passing (5s)
```

### Step 3: Generate Report

```bash
npm run test:report
open cypress/reports/mochawesome.html
```

### Step 4: Document Results

Use report to fill UAT checklist:

| Scenario | Status | Response Code | Notes |
|----------|--------|---------------|-------|
| Success Payment | ✅ PASS | 200 | orderId returned |
| Invalid Field | ✅ PASS | 400 | Error message correct |
| ... | ... | ... | ... |

### Step 5: Submit to DANA

- ✅ Export HTML report
- ✅ Include screenshots/videos if needed
- ✅ Send to DANA support for approval

## 🐛 Troubleshooting

### Tests Failing with "Network Error"

**Problem:** Cannot connect to API

**Solution:**
```bash
# Check API is running
curl https://be-dana.vercel.app/api/v1/auth/health

# Or test locally
ENVIRONMENT=local npm run test:open
```

### JWT Token Expired

**Problem:** 401 Unauthorized errors

**Solution:**
Update JWT token in `cypress.config.js`:
```javascript
env: {
  jwtToken: 'new_token_here'
}
```

### Tests Timeout

**Problem:** Tests hang or timeout

**Solution:**
Increase timeout in `cypress.config.js`:
```javascript
defaultCommandTimeout: 20000,  // 20 seconds
requestTimeout: 20000,
responseTimeout: 20000
```

### Video Recording Issues

**Problem:** Videos not generated

**Solution:**
```javascript
// In cypress.config.js
video: true,  // Enable video
videosFolder: 'cypress/videos'
```

### Can't See Test Runner

**Problem:** `npm run test:open` doesn't open GUI

**Solution:**
```bash
# Install Cypress binary manually
npx cypress install

# Verify installation
npx cypress verify

# Try again
npm run test:open
```

## 📝 Writing New Tests

### Template

```javascript
describe('My Test Suite', () => {

  beforeEach(() => {
    // Setup before each test
    cy.healthCheck()
  })

  it('Should do something', () => {
    cy.logScenario('Test Name', 'Description')

    cy.createOrder({
      nominal: 10000,
      email: 'test@example.com'
    }).then((response) => {
      expect(response.status).to.equal(200)
      expect(response.body.data).to.have.property('orderId')
    })
  })

  after(() => {
    // Cleanup after all tests
    cy.log('Test suite completed')
  })
})
```

### Best Practices

1. **Use cy.logScenario()** - Clear test description
2. **Check response.status** - Validate HTTP status
3. **Use expect()** - Assert expected values
4. **Handle errors** - Use failOnStatusCode: false
5. **Clean up** - Use after() hooks
6. **Unique data** - Use cy.generateTestId()

## 🔐 Security Notes

### Sensitive Data

❌ **DON'T commit:**
- Real JWT tokens
- Production credentials
- Private keys

✅ **DO:**
- Use test/sandbox credentials
- Store secrets in environment variables
- Rotate tokens regularly

### Environment Variables

```bash
# Set via command line
CYPRESS_jwtToken=xxx npm test

# Or create cypress.env.json (gitignored)
{
  "jwtToken": "your_token",
  "apiKey": "your_key"
}
```

## 📞 Support

### Issues

- Cypress not working? Check: https://docs.cypress.io/
- API issues? See: `../DANA_TROUBLESHOOTING.md`
- Test failing? Check logs in console

### Contact

- DANA Support: sandbox-support@dana.id
- GitHub Issues: https://github.com/saefulmuminin/be-dana/issues

## 🎓 Learning Resources

- [Cypress Documentation](https://docs.cypress.io/)
- [API Testing Guide](https://docs.cypress.io/guides/guides/network-requests)
- [Best Practices](https://docs.cypress.io/guides/references/best-practices)

---

**Happy Testing! 🚀**

Generated for: BAZNAS Cinta Zakat - DANA Payment Integration
Last Updated: 2026-02-05
