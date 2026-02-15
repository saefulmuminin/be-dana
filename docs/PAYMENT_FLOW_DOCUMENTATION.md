# Payment Flow Documentation

Dokumentasi lengkap alur pembayaran DANA dari create order hingga webhook dan integrasi dengan campaign.

---

## Flow Overview

```
User Input Form
    ↓
POST /api/v1/dana/create-order
    ↓
Insert to adm_campaign_donasi (status: menunggu)
    ↓
Call DANA API → Get checkoutUrl
    ↓
Return checkoutUrl to Frontend
    ↓
Frontend: my.tradePay({ paymentUrl: checkoutUrl })
    ↓
User Pay in DANA App
    ↓
DANA Send Webhook → POST /api/v1/dana/webhook
    ↓
Update adm_campaign_donasi (status: berhasil)
    ↓
Campaign total_terkumpul updated ✅
    ↓
Muzaki appears in campaign detail ✅
```

---

## 1. Create Order

**Endpoint:** `POST /api/v1/dana/create-order`

**Request:**
```json
{
  "nominal": 10000,
  "email": "user@example.com",
  "campaign_id": 67,
  "nama_lengkap": "John Doe",
  "doa_muzaki": "Semoga berkah",
  "tipe_zakat": "zakat",
  "hamba_allah": "N"
}
```

**Process:**
1. Validate input data
2. Generate `order_id` (e.g., `DANA-20260215123456-ABC123`)
3. Calculate `biaya_admin` and `total_bayar`
4. **Insert to `adm_campaign_donasi`** with status `menunggu`
5. Call DANA API to get `checkoutUrl`
6. Return response with `checkoutUrl`

**Response:**
```json
{
  "status": "success",
  "data": {
    "orderId": "DANA-20260215123456-ABC123",
    "tradeNO": "2026021512345612345",
    "checkoutUrl": "https://m.dana.id/m/portal/payh5?tradeNO=xxx",
    "amount": 10000,
    "status": "pending"
  }
}
```

**Database Record Created:**
```sql
INSERT INTO adm_campaign_donasi (
  campaign_id,      -- Campaign yang dipilih
  order_id,         -- Order ID internal
  nama_lengkap,     -- Nama donor
  email,            -- Email donor
  nominal,          -- Jumlah donasi
  status,           -- 'menunggu'
  hamba_allah,      -- 'Y' untuk anonymous
  doa_muzaki,       -- Pesan/doa
  tgl_donasi,       -- Tanggal create order
  created_date      -- Timestamp
) VALUES (...)
```

---

## 2. User Payment

**Frontend Process:**
```javascript
// Mini App frontend
my.tradePay({
  paymentUrl: checkoutUrl, // From backend response
  success: (res) => {
    // Payment initiated successfully
    // Wait for webhook to confirm
  },
  fail: (err) => {
    // Handle payment failure
  }
});
```

**User Actions:**
1. DANA SDK opens payment popup
2. User enters PIN
3. Payment processed by DANA
4. **DANA sends webhook to backend**

---

## 3. Webhook Processing

**Endpoint:** `POST /api/v1/dana/webhook` or `POST /v1.0/debit/notify`

**DANA Request:**
```json
{
  "originalPartnerReferenceNo": "DANA-20260215123456-ABC123",
  "originalReferenceNo": "2026021512345612345",
  "merchantId": "216610000000045289850",
  "latestTransactionStatus": "SUCCESS",
  "amount": {
    "value": "10000.00",
    "currency": "IDR"
  },
  "transactionStatusDesc": "Payment successful",
  "additionalInfo": {
    "paymentInfo": {
      "paidTime": "2026-02-15T12:35:00+07:00"
    }
  }
}
```

**Process:**
1. Extract `orderId` from webhook payload
2. Find donation record in `adm_campaign_donasi`
3. **Update donation status:**
   - `status` = `'berhasil'` (if SUCCESS)
   - `dana_status` = `'SUCCESS'`
   - `dana_paid_at` = current timestamp
   - `dana_reference_no` = DANA reference number
4. Log webhook to `log_dana_webhook`
5. Trigger SIMBA sync (if needed)

**Code Reference:** [dana_payment_service.py:1275](../src/services/dana_payment_service.py#L1275)

**SQL Update:**
```sql
UPDATE adm_campaign_donasi
SET
  dana_reference_no = %s,
  dana_status = 'SUCCESS',
  status = 'berhasil',
  dana_paid_at = NOW(),
  updated_date = NOW()
WHERE order_id = %s
```

**Response to DANA:**
```json
{
  "responseCode": "2005600",
  "responseMessage": "Successful"
}
```

---

## 4. Campaign Integration

### How Donations Appear in Campaign

**Query in CampaignModel:**
```sql
SELECT
  c.*,
  COALESCE(SUM(CASE WHEN d.status = 'berhasil' THEN d.nominal ELSE 0 END), 0) as total_terkumpul,
  COUNT(CASE WHEN d.status = 'berhasil' THEN 1 END) as jumlah_muzaki
FROM adm_campaign c
LEFT JOIN adm_campaign_donasi d
  ON c.id = d.campaign_id
  AND d.is_delete = 'N'
WHERE c.is_active = 'Y'
  AND c.is_delete = 'N'
  AND c.status = 'publish'
GROUP BY c.id
```

**Key Points:**
- ✅ Only counts donations with `status = 'berhasil'`
- ✅ Excludes soft-deleted records (`is_delete = 'N'`)
- ✅ Real-time aggregation (no caching)

### Muzaki List in Campaign Detail

**Query:**
```sql
SELECT
  CASE
    WHEN hamba_allah = 'Y' THEN 'Hamba Allah'
    ELSE nama_lengkap
  END as nama_muzaki,
  nominal as total_zakat,
  created_date as tgl_donasi,
  doa_muzaki
FROM adm_campaign_donasi
WHERE campaign_id = %s
  AND status = 'berhasil'
  AND is_delete = 'N'
ORDER BY created_date DESC
LIMIT 100
```

**Response Example:**
```json
{
  "list_muzaki": [
    {
      "nama_muzaki": "Hamba Allah",
      "total_zakat": "10000",
      "tgl_donasi": "2026-02-15 12:35:00",
      "doa_muzaki": "Semoga berkah"
    }
  ]
}
```

---

## 5. Status Mapping

### DANA Status → Internal Status

| DANA Status | Internal Status | Database Status | Description |
|-------------|-----------------|-----------------|-------------|
| `PENDING` | `pending` | `menunggu` | Waiting for payment |
| `SUCCESS` | `success` | `berhasil` | Payment successful ✅ |
| `FAILED` | `failed` | `dibatalkan` | Payment failed |
| `CANCELLED` | `cancelled` | `dibatalkan` | User cancelled |
| `EXPIRED` | `expired` | `dibatalkan` | Payment expired |

**Code Reference:**
- [donation_model.py:11-26](../src/models/donation_model.py#L11-L26) - Status mapping constants
- [donation_model.py:166-194](../src/models/donation_model.py#L166-L194) - `updateDanaStatusRef()` method

---

## 6. Troubleshooting

### Problem: Donations Not Appearing in Campaign

**Symptoms:**
- `total_terkumpul` shows 0
- `list_muzaki` is empty
- Donations exist in database

**Root Cause:**
Donations have status `menunggu` instead of `berhasil`

**Solution:**
1. Check if webhook was received:
   ```sql
   SELECT * FROM log_dana_webhook
   WHERE order_id = 'DANA-XXX'
   ORDER BY created_date DESC;
   ```

2. Check donation status:
   ```sql
   SELECT order_id, status, dana_status, dana_paid_at
   FROM adm_campaign_donasi
   WHERE order_id = 'DANA-XXX';
   ```

3. Manual update (for testing):
   ```sql
   UPDATE adm_campaign_donasi
   SET status = 'berhasil',
       dana_status = 'SUCCESS',
       dana_paid_at = NOW()
   WHERE order_id = 'DANA-XXX';
   ```

### Problem: Webhook Not Received

**Possible Causes:**
1. **Webhook URL not configured** in DANA dashboard
2. **Network/firewall** blocking DANA servers
3. **SSL certificate** issues
4. **Signature verification** failing

**Debug Steps:**
1. Check webhook logs:
   ```sql
   SELECT * FROM log_dana_webhook
   ORDER BY created_date DESC LIMIT 10;
   ```

2. Check API logs:
   ```sql
   SELECT * FROM log_api
   WHERE name LIKE 'DANA_PAYMENT_%'
   ORDER BY created_date DESC LIMIT 10;
   ```

3. Test webhook endpoint manually:
   ```bash
   curl -X POST http://localhost:8899/api/v1/dana/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "originalPartnerReferenceNo": "DANA-20260215123456-ABC123",
       "latestTransactionStatus": "SUCCESS",
       "amount": {"value": "10000.00", "currency": "IDR"}
     }'
   ```

---

## 7. Testing

### Manual Testing Script

See [test_donation_flow.py](../scripts/test_donation_flow.py) for complete testing script.

**Quick Test:**
```python
from src.services.dana_payment_service import DanaPaymentService

service = DanaPaymentService()

# 1. Create order
order_result = service.createOrder({
    "nominal": 10000,
    "email": "test@example.com",
    "campaign_id": 67,
    "nama_lengkap": "Test User",
    "tipe_zakat": "zakat",
    "hamba_allah": "N"
})

order_id = order_result[0]['data']['orderId']
print(f"Order created: {order_id}")

# 2. Simulate webhook (payment success)
webhook_result = service.webhook({
    "originalPartnerReferenceNo": order_id,
    "latestTransactionStatus": "SUCCESS",
    "amount": {"value": "10000.00", "currency": "IDR"}
})

print(f"Webhook processed: {webhook_result}")

# 3. Verify donation status
from src.models.donation_model import DonationModel
donation_model = DonationModel()
donation = donation_model.findByOrderId(order_id)
print(f"Donation status: {donation['status']}")
```

---

## 8. Database Schema Reference

### adm_campaign_donasi

Key fields for payment flow:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Primary key |
| `campaign_id` | integer | FK to adm_campaign |
| `order_id` | varchar | Internal order ID |
| `partner_reference_no` | varchar | Partner reference |
| `dana_reference_no` | varchar | DANA reference from webhook |
| `dana_status` | varchar | DANA payment status |
| `status` | enum | Internal status (berhasil/menunggu/dibatalkan) |
| `nama_lengkap` | varchar | Donor name |
| `email` | varchar | Donor email |
| `nominal` | bigint | Donation amount |
| `hamba_allah` | enum | Anonymous flag (Y/N) |
| `doa_muzaki` | varchar | Donor's prayer/message |
| `dana_paid_at` | timestamp | Payment timestamp |
| `tgl_donasi` | date | Donation date |
| `created_date` | timestamp | Record creation time |

### Related Tables

- `adm_campaign` - Campaign master data
- `log_dana_webhook` - Webhook event logs
- `log_dana_transaction` - Transaction logs
- `log_api` - API call logs

---

## 9. Production Checklist

Before going live, ensure:

- [ ] DANA webhook URL configured in DANA dashboard
- [ ] DANA credentials (CLIENT_ID, PRIVATE_KEY, MERCHANT_ID) set in production
- [ ] SSL certificate valid and trusted
- [ ] Database backup enabled
- [ ] Monitoring/alerting for failed webhooks
- [ ] Log retention policy configured
- [ ] Test payment flow end-to-end in sandbox
- [ ] Documented rollback procedures
- [ ] Support team trained on troubleshooting

---

## 10. API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/dana/create-order` | POST | Create payment order |
| `/api/v1/dana/webhook` | POST | Receive DANA webhook |
| `/v1.0/debit/notify` | POST | SNAP API webhook (alias) |
| `/api/v1/dana/query-payment/<orderId>` | GET | Check payment status |
| `/api/v1/kegiatan/index` | POST | List campaigns with total_terkumpul |
| `/api/v1/kegiatan/detail` | POST | Get campaign detail with muzaki list |

---

## Contact & Support

For issues or questions:
- Repository: https://github.com/saefulmuminin/be-dana
- Documentation: `/docs` folder
- Logs: Check `log_dana_webhook`, `log_dana_transaction`, `log_api` tables
