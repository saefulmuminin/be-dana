# DANA Create Order - Improved Implementation

## File: src/services/dana_service.py - Updated create_order()

Berikut adalah improved version dari `create_order()` dengan semua perbaikan untuk match GoPay logic:

```python
def create_order(self, data):
    """
    Create donation order dan generate DANA payment URL
    IMPROVED VERSION: Sesuai dengan GoPay logic
    
    Flow:
    1. Validate input (enhanced validation)
    2. Fetch payment method + campaign details
    3. Calculate fees based on campaign & method
    4. Save complete donation data
    5. Create payment request ke DANA dengan lengkap
    6. Return payment URL
    
    Request params:
    - access_token: DANA accessToken dari apply_token
    - nominal: donation amount (required)
    - email: user email (required)
    - metode_id: payment method ID (default: 2)
    - campaign_id: campaign ID (optional tapi recommended)
    - nama: user full name (optional - fallback: 'Hamba Allah')
    - doa_muzaki: user doa/message (optional)
    - muzaki_id: existing muzaki ID (optional)
    - hamba_allah: anonymous flag (default: 'N')
    - device_id: device type (default: 'web')
    - ip_address: user IP (default: '0.0.0.0')
    - redirect_url: callback URL after payment
    - user_email: email of person making request (for audit)
    """
    try:
        # ===== 1. ENHANCED VALIDATION =====
        
        # Check required fields
        access_token = data.get('access_token')
        nominal = data.get('nominal')
        email = data.get('email')
        metode_id = data.get('metode_id', 2)
        
        if not access_token or not nominal or not email:
            return Response.error("Missing required fields: access_token, nominal, email", 400)
        
        # Validate nominal
        try:
            nominal = float(nominal)
        except (ValueError, TypeError):
            return Response.error("Invalid nominal format - must be numeric", 400)
        
        if nominal <= 0:
            return Response.error("Nominal must be greater than 0", 400)
        
        if nominal > 1000000000:  # Max 1 billion IDR
            return Response.error("Nominal exceeds maximum limit", 400)
        
        # Validate email format (regex basic)
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return Response.error("Invalid email format", 400)
        
        campaign_id = data.get('campaign_id')
        
        # ===== 2. FETCH PAYMENT METHOD =====
        
        metode = self.payment_model.find_by_id(metode_id)
        if not metode:
            return Response.error("Payment method not found", 404)
        
        # ===== 3. FETCH CAMPAIGN (BARU) =====
        
        campaign = None
        if campaign_id:
            # Assuming you have campaign_model
            # from src.models.master_models import RefCampaignModel
            campaign = self.campaign_model.find_by_id(campaign_id)
            if not campaign:
                return Response.error("Campaign not found", 404)
        
        # ===== 4. FEE CALCULATION =====
        
        # Operational fee (dari campaign jika ada, atau default 0)
        percent_ops = 0
        if campaign and campaign.get('prosen_biayaoperasional'):
            percent_ops = float(campaign.get('prosen_biayaoperasional', 0))
        
        biaya_operasional = nominal * (percent_ops / 100)
        donasi_net = nominal - biaya_operasional
        
        # Admin fee (dari metode pembayaran)
        biaya_admin = 0
        admin_fee_rate = float(metode.get('biaya_admin', 0))
        payment_type = metode.get('payment_type', '')
        
        if payment_type in ['emoney', 'akulaku']:
            biaya_admin = admin_fee_rate * nominal
        else:
            biaya_admin = admin_fee_rate
        
        # Total amount to charge
        total_amount = nominal + biaya_admin
        
        # ===== 5. PREPARE DONATION DATA =====
        
        # Generate IDs
        order_id = f"ORDER-{uuid.uuid4().hex[:12].upper()}"
        partner_ref_no = f"CINTA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Get user name (improved logic)
        nama_lengkap = data.get('nama', '').strip()
        if not nama_lengkap or nama_lengkap.lower() == 'hamba allah':
            nama_lengkap = 'Hamba Allah'
        
        # Get user type
        tipe_zakat = campaign.get('tipe', 'infak') if campaign else 'infak'
        
        # Get created_by
        created_by = data.get('user_email', data.get('email', 'system'))
        
        # Prepare donation record (COMPLETE)
        donation_data = {
            'order_id': order_id,
            'partner_reference_no': partner_ref_no,
            'muzaki_id': data.get('muzaki_id'),
            'campaign_id': campaign_id,
            'metode_id': metode_id,
            'email': email,
            'nama_lengkap': nama_lengkap,              # ✅ ADD: Store nama
            'tipe_zakat': tipe_zakat,                  # ✅ ADD: Store tipe_zakat
            'doa_muzaki': data.get('doa_muzaki', ''),  # ✅ ADD: Store doa
            'nominal': nominal,
            'biaya_operasional': biaya_operasional,
            'biaya_admin': biaya_admin,
            'donasi_net': donasi_net,
            'hamba_allah': data.get('hamba_allah', 'N'),
            'npwz': data.get('npwz', ''),
            'status': 'pending',
            'access_token': access_token,              # Store untuk OTT & webhook
            'created_by': created_by                   # ✅ IMPROVE: Track user
        }
        
        # Create donation record
        self.donation_model.create(donation_data)
        
        # ===== 6. PREPARE DANA PAYMENT REQUEST (LENGKAP) =====
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Prepare item name & details
        item_name = f"Donation - {campaign.get('name')}" if campaign else f"Donation - {campaign_id or 'General'}"
        item_brand = campaign.get('tipe', '') if campaign else ''
        
        # Split nama for first/last name
        nama_parts = nama_lengkap.split(' ', 1)
        first_name = nama_parts[0] if len(nama_parts) > 0 else 'Muzaki'
        last_name = nama_parts[1] if len(nama_parts) > 1 else ''
        
        payment_request = {
            "amount": str(int(total_amount)),
            "currency": "IDR",
            "partnerReferenceNo": partner_ref_no,
            "merchantId": self.merchant_id,
            "apikey": self.partner_id,
            "additionalInfo": {
                # ✅ ADD: Full customer details (sesuai GoPay)
                "customerDetails": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "phone": data.get('phone', ''),
                    "nationality": "ID"
                },
                "deviceId": data.get('device_id', 'web'),
                "ipAddress": data.get('ip_address', '0.0.0.0')
            },
            "urlParam": {
                "url": data.get('redirect_url', f"https://app.cintazakat.id/payment/result?order={order_id}"),
                "type": "NOTIFICATION"
            },
            # ✅ IMPROVED: Complete item data (sesuai GoPay)
            "items": [
                {
                    "id": str(campaign_id) if campaign_id else order_id,
                    "name": item_name,
                    "quantity": 1,
                    "price": str(int(total_amount)),
                    "brand": item_brand,
                    "category": item_brand,
                    "metode": str(metode_id),
                    "merchantName": "BAZNAS - Cinta Zakat",
                    "url": campaign.get('url', '') if campaign else ""
                }
            ]
        }
        
        # Generate signature
        body_str = json.dumps(payment_request, separators=(',', ':'), sort_keys=True)
        signature = self._generate_signature(timestamp, "POST", "/gateway/api/debit/payment/createRequest", body_str)
        headers = self._get_headers(timestamp, signature)
        headers["Authorization"] = f"Bearer {access_token}"
        
        # Call DANA Create Payment API
        response = requests.post(
            self.payment_url,
            json=payment_request,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            self.donation_model.update_status(order_id, 'failed')
            return Response.error(f"DANA API Error: {response.text}", response.status_code)
        
        result = response.json()
        
        if result.get('responseCode') != '2005400':
            self.donation_model.update_status(order_id, 'failed')
            return Response.error(f"DANA Error: {result.get('responseMessage')}")
        
        # Store DANA reference numbers
        reference_no = result.get('referenceNo')
        web_redirect_url = result.get('webRedirectUrl')
        
        # Update donation dengan DANA reference
        self.donation_model.update_dana_refs(order_id, reference_no, web_redirect_url)
        
        # ===== 7. RETURN RESPONSE =====
        
        return Response.success(data={
            "order_id": order_id,
            "partner_reference_no": partner_ref_no,
            "reference_no": reference_no,
            "web_redirect_url": web_redirect_url,
            "breakdown": {
                "nominal": nominal,
                "operational_fee": biaya_operasional,
                "admin_fee": biaya_admin,
                "total_charged": total_amount,
                "net_donation": donasi_net
            },
            "customer": {
                "name": nama_lengkap,
                "email": email,
                "anonymous": data.get('hamba_allah', 'N') == 'Y'
            },
            "campaign": {
                "id": campaign_id,
                "name": campaign.get('name') if campaign else None,
                "type": tipe_zakat
            },
            "next_step": "call apply_ott endpoint to get payment token"
        })
        
    except Exception as e:
        return Response.error(f"Create order failed: {str(e)}")
```

---

## File: src/models/donation_model.py - Updates

Tambahkan kolom baru di create() method:

```python
def create(self, data):
    """
    Create a donation record dengan data LENGKAP
    """
    required_fields = ['nominal', 'metode_id']
    for field in required_fields:
        if field not in data:
            pass

    checksum = self.generate_checksum(str(data.get('email')) + str(data.get('nominal')))
    uuid_val = self.generate_uuid()

    with self.conn.cursor() as cursor:
        sql = f"""
            INSERT INTO {self.table_name} 
            (order_id, muzaki_id, campaign_id, metode_id, email, nama_lengkap, 
             tipe_zakat, nominal, biaya_operasional, biaya_admin, donasi_net, 
             doa_muzaki, hamba_allah, npwz, tgl_donasi, status, partner_reference_no,
             checksum, uuid, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data.get('order_id'),
            data.get('muzaki_id'),
            data.get('campaign_id'),
            data.get('metode_id'),
            data.get('email'),
            data.get('nama_lengkap'),              # ✅ NEW
            data.get('tipe_zakat'),                # ✅ NEW
            data.get('nominal'),
            data.get('biaya_operasional', 0),
            data.get('biaya_admin', 0),
            data.get('donasi_net', 0),
            data.get('doa_muzaki', ''),            # ✅ NEW
            data.get('hamba_allah', 'N'),
            data.get('npwz', ''),
            data.get('tgl_donasi', datetime.now()),
            data.get('status', 'pending'),
            data.get('partner_reference_no'),      # ✅ NEW
            checksum,
            uuid_val,
            data.get('created_by', 'system'),      # ✅ NEW
            datetime.now()
        ))
        self.conn.commit()
        return cursor.lastrowid
```

---

## Database Schema Migration

```sql
-- Add missing columns to donations table
ALTER TABLE donations ADD COLUMN (
    nama_lengkap VARCHAR(255),
    tipe_zakat VARCHAR(50),
    doa_muzaki LONGTEXT,
    partner_reference_no VARCHAR(100) UNIQUE
) AFTER email;

-- If these columns don't exist yet:
-- ALTER TABLE donations ADD COLUMN dana_reference_no VARCHAR(100) AFTER partner_reference_no;
-- ALTER TABLE donations ADD COLUMN dana_web_redirect_url TEXT;
-- ALTER TABLE donations ADD COLUMN dana_status VARCHAR(50);
-- ALTER TABLE donations ADD COLUMN access_token LONGTEXT;

-- Update created_by to not hardcoded
ALTER TABLE donations MODIFY created_by VARCHAR(255) NOT NULL DEFAULT 'system';
```

---

## Request/Response Example

### Request (dengan semua data):
```json
{
    "access_token": "dana_access_token_abc123",
    "nominal": 500000,
    "email": "muzaki@example.com",
    "metode_id": 2,
    "campaign_id": 123,
    "nama": "Ahmad Ramadan",
    "doa_muzaki": "Semoga bermanfaat untuk yang membutuhkan",
    "muzaki_id": 456,
    "hamba_allah": "N",
    "device_id": "web",
    "ip_address": "192.168.1.1",
    "redirect_url": "https://app.cintazakat.id/payment/result",
    "phone": "081234567890",
    "user_email": "staff@baznas.or.id"
}
```

### Response (dengan breakdown lengkap):
```json
{
    "status_code": 200,
    "status": "success",
    "message": "Order created successfully",
    "data": {
        "order_id": "ORDER-ABC123DEF456",
        "partner_reference_no": "CINTA-20250127103045-XYZ789",
        "reference_no": "2020102977770000000009",
        "web_redirect_url": "https://pjsp.com/universal?bizNo=REF123",
        "breakdown": {
            "nominal": 500000,
            "operational_fee": 12500,
            "admin_fee": 2500,
            "total_charged": 502500,
            "net_donation": 487500
        },
        "customer": {
            "name": "Ahmad Ramadan",
            "email": "muzaki@example.com",
            "anonymous": false
        },
        "campaign": {
            "id": 123,
            "name": "Bantuan Kemanusiaan",
            "type": "infak"
        },
        "next_step": "call apply_ott endpoint to get payment token"
    }
}
```

---

## Summary of Changes

| No | Change | Type | File |
|---|--------|------|------|
| 1 | Add enhanced validation (email, nominal) | Code | dana_service.py |
| 2 | Fetch campaign details | Code | dana_service.py |
| 3 | Store `nama_lengkap` | Code + DB | dana_service.py + donations table |
| 4 | Store `tipe_zakat` | Code + DB | dana_service.py + donations table |
| 5 | Store `doa_muzaki` | Code + DB | dana_service.py + donations table |
| 6 | Send customerDetails to DANA | Code | dana_service.py |
| 7 | Send complete items data | Code | dana_service.py |
| 8 | Better created_by tracking | Code + DB | dana_service.py + donations table |
| 9 | Improved response breakdown | Code | dana_service.py |
| 10 | Better error messages | Code | dana_service.py |

---

## Testing Checklist

- [ ] Test dengan semua fields required
- [ ] Test dengan missing optional fields
- [ ] Test email validation (invalid format)
- [ ] Test nominal validation (0, negative, too large)
- [ ] Test campaign lookup (valid & invalid)
- [ ] Test payment method lookup (valid & invalid)
- [ ] Test fee calculation (emoney vs flat)
- [ ] Test DANA API response handling
- [ ] Test database storage (verify all columns)
- [ ] Test response structure (breakdown, customer, campaign)
- [ ] Test with anonymous donation (hamba_allah = 'Y')
- [ ] Test with existing muzaki_id
