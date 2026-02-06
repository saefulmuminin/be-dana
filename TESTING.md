# Testing Guide - DANA Payment API

Complete testing documentation untuk DANA Payment Integration.

## 🧪 Testing Tools

Project ini menggunakan dua tools untuk testing:

### 1. Postman (Manual Testing)
- 📦 Collection dengan 30+ endpoints
- 🎯 UAT test scenarios
- 📝 Documentation & examples
- 👉 See: [postman/README.md](postman/README.md)

### 2. Cypress (Automated Testing)
- 🤖 Automated UAT testing
- 🔄 CI/CD integration ready
- 📊 HTML test reports
- 👉 See: [cypress/README.md](cypress/README.md)

## 🚀 Quick Start

### Setup Postman Testing

```bash
# 1. Open Postman
# 2. Import collection
postman/DANA_API_Complete_Collection.postman_collection.json

# 3. Import environment
postman/Production.postman_environment.json

# 4. Start testing!
```

### Setup Cypress Testing

```bash
# 1. Install dependencies
npm install

# 2. Run tests interactively
npm run test:open

# 3. Or run headless
npm run test:uat
```

## 📋 UAT Test Scenarios

### Direct Debit Payment (7 Scenarios)

| # | Scenario | Method | Expected Response | Status |
|---|----------|--------|-------------------|---------|
| 1 | Success Payment | POST /create-order | 200, orderId returned | Ready |
| 2 | Invalid Field | POST /create-order | 400, error message | ✅ Verified |
| 3 | General Error | POST /create-order | 500, error message | Ready |
| 4 | Not Permitted | POST /create-order | 403, not permitted | Ready |
| 5 | Invalid Merchant | POST /create-order | 404, invalid merchant | Ready |
| 6 | Inconsistent Request | POST /create-order | 409, inconsistent | Ready |
| 7 | Server Error | POST /create-order | 500, server error | Ready |

### Payment Finish Notify (3 Scenarios)

| # | Scenario | Method | Expected Response | Status |
|---|----------|--------|-------------------|---------|
| 1 | Success Notify | POST /v1.0/debit/notify | 200, acknowledged | Ready |
| 2 | Server Error | POST /v1.0/debit/notify | 500, error | Ready |
| 3 | Cancelled Notify | POST /v1.0/debit/notify | 200, acknowledged | Ready |

## 🎯 Testing Workflows

### Workflow 1: Manual Testing (Postman)

**Use Case:** Quick testing, API exploration, documentation

```
1. Import Postman collection
2. Select environment (Production/Local)
3. Run "Create Order" request
4. Check response → orderId auto-saved
5. Run "Query Payment" → uses saved orderId
6. Run "Finish Payment" → simulate callback
7. Verify status updated
```

**Pros:**
- ✅ Quick and interactive
- ✅ Easy to modify requests
- ✅ Great for debugging
- ✅ Export as documentation

**Cons:**
- ❌ Manual execution
- ❌ Not suitable for CI/CD
- ❌ Time-consuming for repetitive tests

### Workflow 2: Automated Testing (Cypress)

**Use Case:** UAT validation, CI/CD, regression testing

```bash
# Run all UAT tests
npm run test:uat

# Generate report
npm run test:report
open cypress/reports/mochawesome.html

# Submit to DANA
Export report → Send to DANA support
```

**Pros:**
- ✅ Fully automated
- ✅ Repeatable and consistent
- ✅ CI/CD integration
- ✅ HTML reports with screenshots

**Cons:**
- ❌ Initial setup required
- ❌ Requires Node.js
- ❌ Less flexible for exploration

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: DANA API UAT Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Run Cypress UAT Tests
        run: npm run test:uat

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: cypress-results
          path: |
            cypress/videos
            cypress/screenshots
            cypress/reports
```

### Vercel Integration

```json
// vercel.json
{
  "buildCommand": "echo 'No build needed'",
  "devCommand": "python app.py",
  "framework": null,
  "installCommand": "pip install -r requirements.txt && npm install",
  "ignoreCommand": "git diff HEAD^ HEAD --quiet -- '*.py' '*.json'"
}
```

## 📊 Test Reports

### Postman Reports

**Newman CLI (for automation):**

```bash
# Install newman
npm install -g newman newman-reporter-htmlextra

# Run collection
newman run postman/DANA_API_Complete_Collection.postman_collection.json \
  -e postman/Production.postman_environment.json \
  -r htmlextra \
  --reporter-htmlextra-export reports/postman-report.html
```

### Cypress Reports

**Mochawesome (included):**

```bash
# Run with report
npm run test:report

# Open report
open cypress/reports/mochawesome.html
```

**Report includes:**
- ✅ Test pass/fail status
- ⏱️ Execution time
- 📸 Failure screenshots
- 📹 Video recordings
- 📝 Detailed logs

## 🐛 Debugging Tests

### Postman Debugging

```javascript
// Pre-request Script
console.log('Request:', pm.request);
console.log('Environment:', pm.environment.toObject());

// Test Script
console.log('Response:', pm.response.json());
console.log('Status:', pm.response.code);
```

### Cypress Debugging

```javascript
// Add breakpoint
cy.debug()

// Pause test
cy.pause()

// Log data
cy.log('My debug message', data)

// Console log
cy.then(() => {
  console.log('Debug:', data)
})
```

**Interactive Mode:**
```bash
npm run test:open
# Click test → Opens browser
# Browser DevTools available
# Step through tests
```

## 📝 UAT Checklist

Before submitting to DANA:

### Pre-Testing
- [ ] Verify all environment variables set
- [ ] Confirm API is accessible
- [ ] Check JWT token is valid
- [ ] Review test data

### Testing
- [ ] Run all Postman scenarios manually
- [ ] Run Cypress automated tests
- [ ] Verify all tests pass
- [ ] Check for unexpected errors

### Documentation
- [ ] Generate test reports
- [ ] Screenshot important results
- [ ] Document any issues found
- [ ] Note DANA API responses

### Submission
- [ ] Export Postman collection
- [ ] Include Cypress HTML report
- [ ] Add screenshots/videos
- [ ] Fill UAT form for DANA

## 🔐 Security Considerations

### Test Data
- ✅ Use test/sandbox credentials
- ✅ Use dummy email addresses
- ✅ Use small test amounts (e.g., 10000)
- ❌ Don't use production credentials
- ❌ Don't use real email addresses
- ❌ Don't commit sensitive data

### Credentials Management
```bash
# Use environment variables
export DANA_CLIENT_ID="..."
export DANA_CLIENT_SECRET="..."

# Or create .env.test (gitignored)
DANA_ENV=sandbox
DANA_DEV_MODE=true
```

## 📞 Support & Resources

### Documentation
- [Postman Testing Guide](postman/README.md)
- [Cypress Testing Guide](cypress/README.md)
- [DANA Troubleshooting](DANA_TROUBLESHOOTING.md)
- [Vercel Setup](VERCEL_SETUP.md)

### External Resources
- [Postman Learning Center](https://learning.postman.com/)
- [Cypress Documentation](https://docs.cypress.io/)
- [DANA Developer Docs](https://developers.dana.id/)

### Contact
- DANA Support: sandbox-support@dana.id
- GitHub Issues: https://github.com/saefulmuminin/be-dana/issues

## 🎯 Next Steps

1. **Choose Your Tool:**
   - Quick testing? → Use Postman
   - Automated UAT? → Use Cypress
   - Both? → Even better!

2. **Run Tests:**
   - Follow quick start guide above
   - Run through all scenarios
   - Document results

3. **Submit to DANA:**
   - Export test reports
   - Include documentation
   - Contact DANA support

4. **After DANA Approval:**
   - Update test data if needed
   - Run regression tests
   - Setup CI/CD pipeline

---

**Happy Testing! 🧪**

Generated for: BAZNAS Cinta Zakat - DANA Payment Integration
Last Updated: 2026-02-05
