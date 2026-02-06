# Postman Collection - DANA API Testing

## 📦 Files

1. **DANA_API_Complete_Collection.postman_collection.json** - Complete API collection
2. **Production.postman_environment.json** - Production environment (Vercel)
3. **Local.postman_environment.json** - Local development environment

## 🚀 Quick Start

### 1. Import ke Postman

**Import Collection:**
1. Buka Postman
2. Click **Import** button
3. Drag & drop atau pilih file: `DANA_API_Complete_Collection.postman_collection.json`

**Import Environments:**
1. Click **Import** button lagi
2. Import kedua environment files:
   - `Production.postman_environment.json`
   - `Local.postman_environment.json`

### 2. Pilih Environment

Di top-right corner Postman, pilih environment:
- **DANA API - Production** → untuk testing di Vercel
- **DANA API - Local Development** → untuk testing local (port 5000)

### 3. Test Basic Flow

**Step 1: Health Check**
```
GET /api/v1/auth/health
```
Pastikan API responding

**Step 2: Create Order**
```
POST /api/v1/dana/create-order
Body:
{
  "nominal": 10000,
  "email": "test@example.com",
  "nama_lengkap": "Test User",
  "campaign_id": 1
}
```
- ✅ Postman akan auto-save `order_id` dan `trade_no` ke environment variables
- ✅ Variables ini bisa digunakan di request berikutnya

**Step 3: Query Payment**
```
GET /api/v1/dana/query-payment/{{order_id}}
```
Menggunakan `{{order_id}}` yang auto-saved dari Step 2

**Step 4: Finish Payment (Simulate Callback)**
```
POST /api/v1/dana/finish-payment
Body:
{
  "orderId": "{{order_id}}",
  "resultCode": "9000"
}
```

## 📁 Collection Structure

### 1. Health & Status
- ✅ Health Check - API status check

### 2. Auth
- 🔐 Generate OAuth URL
- 🔐 Apply Token
- 🔐 Seamless Login
- 🔐 Refresh Token

### 3. DANA Payment (Main Flow)
- 💰 **Create Order** - Create payment order (auto-saves orderId & tradeNO)
- 🔍 Query Payment Status - Check payment status
- ❌ Cancel Order - Cancel unpaid order
- ✅ Finish Payment - Payment completion callback
- 🔔 Webhook - DANA notification endpoint

### 4. SNAP API (ASPI Standard)
- 🔔 Debit Notify - SNAP API webhook
- 🔍 Debit Status Query - SNAP API query

### 5. User Profile (Protected)
- 👤 Get Profile - Requires Bearer token
- ✏️ Update Profile - Requires Bearer token
- 📜 Transaction History - Requires Bearer token
- 📄 Transaction Detail - Requires Bearer token
- 📧 Send History Email - Requires Bearer token

### 6. Payment Channels
- 💳 Get Payment Channels

### 7. Test Scenarios (UAT)
- ✅ Scenario 1: Success Payment
- ❌ Scenario 2: Invalid Amount (0)
- ❌ Scenario 3: Missing Required Field
- 💰 Scenario 4: Large Amount
- ✅ Scenario 5: Payment Success Callback
- ❌ Scenario 6: Payment Failed Callback
- 🚫 Scenario 7: User Cancelled
- ❓ Scenario 8: Query Non-existent Order

## 🔑 Environment Variables

### Auto-Saved Variables
Postman akan auto-save variables ini setelah create order:
- `order_id` - Order ID dari create-order response
- `trade_no` - Trade number untuk my.tradePay()

### Pre-configured Variables
- `base_url` - API base URL (Production atau Local)
- `jwt_token` - Bearer token untuk protected endpoints
- `merchant_id` - DANA merchant ID
- `client_id` - DANA client ID
- `channel_id` - DANA channel ID

## 🧪 Testing Workflow

### Complete Payment Flow Test

1. **Create Order**
   ```
   POST /api/v1/dana/create-order
   ```
   Expected: `orderId` dan `tradeNO` returned

2. **Query Status (Pending)**
   ```
   GET /api/v1/dana/query-payment/{{order_id}}
   ```
   Expected: Status = "pending"

3. **Simulate Payment Success**
   ```
   POST /api/v1/dana/finish-payment
   Body: { "orderId": "{{order_id}}", "resultCode": "9000" }
   ```
   Expected: Status = "success"

4. **Query Status (Success)**
   ```
   GET /api/v1/dana/query-payment/{{order_id}}
   ```
   Expected: Status = "success"

### UAT Testing (Run All Scenarios)

Folder **Test Scenarios (UAT)** berisi 8 test scenarios:

1. ✅ Run semua scenario dari Scenario 1 - 8
2. 📊 Document hasil setiap scenario
3. ✅ Pastikan semua PASS sebelum production

Expected Results:
```
✅ Scenario 1: Success Payment → PASS
✅ Scenario 2: Invalid Amount → PASS (returns error)
✅ Scenario 3: Missing Field → PASS (returns error)
✅ Scenario 4: Large Amount → PASS
✅ Scenario 5: Success Callback → PASS
✅ Scenario 6: Failed Callback → PASS
✅ Scenario 7: User Cancelled → PASS
✅ Scenario 8: Non-existent Order → PASS (returns not found)
```

## 🔐 Protected Endpoints

Endpoints di folder **User Profile** memerlukan Bearer token.

### Cara Setup Bearer Token:

**Option 1: Collection Variable (Sudah di-set)**
- JWT token sudah di-set di collection variables
- Auto-applied untuk protected endpoints

**Option 2: Manual di Header**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Option 3: Generate New Token**
1. Login via seamless-login endpoint
2. Copy JWT token dari response
3. Update `jwt_token` variable di environment

## 📝 Result Codes

### Payment Result Codes (finish-payment):
- `9000` - Payment success ✅
- `4000` - Payment failed ❌
- `6001` - User cancelled 🚫
- `6002` - Network error 📡
- `8000` - Processing ⏳
- `6004` - Unknown result (may be success) ❓

### SNAP API Response Codes:
- `2005400` - Successful ✅
- `4005401` - Invalid Field Format ❌
- `4045401` - Transaction Not Found ❓

## 🛠️ Development Mode Testing

Jika `DANA_DEV_MODE=true` di backend:

**Create Order Response:**
```json
{
  "status": "success",
  "data": {
    "orderId": "DANA-20260206123456",
    "tradeNO": "DANA-20260206123456",
    "danaApiCalled": false,
    "amount": 10000
  }
}
```

- `danaApiCalled: false` → DANA API di-bypass
- `tradeNO = orderId` → Local ID untuk testing
- Frontend flow bisa di-test tanpa DANA API

## 🎯 Tips & Tricks

### 1. Quick Testing dengan Runner
1. Select collection atau folder
2. Click "Run" button
3. Jalankan multiple requests sekaligus
4. Review results di Runner tab

### 2. Save Response Examples
Setelah dapat response:
1. Click "Save as Example"
2. Dokumentasi response untuk future reference

### 3. Pre-request Scripts
Create Order sudah ada script untuk auto-save variables:
```javascript
// Auto-saves orderId and tradeNO to environment
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set('order_id', jsonData.data.orderId);
    pm.environment.set('trade_no', jsonData.data.tradeNO);
}
```

### 4. Chain Requests
Gunakan `{{variable}}` untuk chain requests:
```
Create Order → Save orderId
Query Payment/{{order_id}} → Use saved orderId
Finish Payment → Use saved orderId
```

## 🐛 Troubleshooting

### Error: "Could not get response"
- ✅ Check base_url di environment
- ✅ Pastikan API server running (local) atau Vercel deployed
- ✅ Check network connectivity

### Error: "Unauthorized" (401)
- ✅ Pastikan jwt_token di environment valid
- ✅ Token mungkin expired, generate new token
- ✅ Check Authorization header format: `Bearer <token>`

### Error: "Order not found"
- ✅ Pastikan order_id variable ter-set
- ✅ Check apakah create-order berhasil
- ✅ Lihat di Console log untuk debug

### Dev Mode Issues
Jika DANA_DEV_MODE=true tapi masih error:
- ✅ Check Vercel environment variables
- ✅ Redeploy Vercel setelah update env
- ✅ Clear backend logs dan test ulang

## 📊 UAT Report Template

Gunakan template ini untuk dokumentasi UAT:

| No | Test Scenario | Expected | Actual | Status |
|----|---------------|----------|--------|--------|
| 1 | Success payment | orderId returned | orderId returned | ✅ PASS |
| 2 | Invalid amount | Error 4005402 | Error 4005402 | ✅ PASS |
| 3 | Missing field | Error message | Error message | ✅ PASS |
| 4 | Large amount | orderId returned | orderId returned | ✅ PASS |
| 5 | Success callback | Status success | Status success | ✅ PASS |
| 6 | Failed callback | Status failed | Status failed | ✅ PASS |
| 7 | User cancelled | Status cancelled | Status cancelled | ✅ PASS |
| 8 | Non-existent | Not found error | Not found error | ✅ PASS |

## 🔗 Related Documentation

- [DANA_TROUBLESHOOTING.md](../DANA_TROUBLESHOOTING.md) - Troubleshooting guide
- [VERCEL_SETUP.md](../VERCEL_SETUP.md) - Vercel deployment guide
- [DANA_SUPPORT_EMAIL.txt](../DANA_SUPPORT_EMAIL.txt) - Support email template

## 📞 Support

Jika ada issue dengan collection:
1. Check troubleshooting section di atas
2. Review [DANA_TROUBLESHOOTING.md](../DANA_TROUBLESHOOTING.md)
3. Contact DANA support jika merchant configuration issue

---

**Happy Testing! 🚀**

Generated for: BAZNAS Cinta Zakat - DANA Payment Integration
Last Updated: 2026-02-05
