"""
DANA Mini Program Payment Service
Untuk integrasi pembayaran di DANA Mini App

Flow Mini Program Payment:
1. User isi form donasi di mini app
2. Mini app call backend /create-order -> backend return orderId + tradeNO
3. Backend call DANA Direct Debit Payment API -> dapat referenceNo
4. Mini app call my.tradePay(tradeNO: referenceNo)
5. DANA SDK handle pembayaran (popup PIN muncul)
6. DANA kirim webhook ke backend untuk update status

API Reference:
- Endpoint: /rest/redirection/v1.0/debit/payment-host-to-host
- Signature: RSA asymmetric (PKCS1_v1_5 + SHA256)
- Response: referenceNo digunakan sebagai tradeNO untuk my.tradePay
"""

from src.models.donation_model import DonationModel
from src.models.master_models import RefPaymentModel, RefCampaignModel
from src.services.simba_service import SimbaService
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime, timezone, timedelta
import os
import uuid
import json
import requests
import hashlib
import base64
import hmac

# RSA Signature imports
try:
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    CRYPTO_AVAILABLE = True
except ImportError:
    try:
        from Cryptodome.Signature import PKCS1_v1_5
        from Cryptodome.Hash import SHA256
        from Cryptodome.PublicKey import RSA
        CRYPTO_AVAILABLE = True
    except ImportError:
        CRYPTO_AVAILABLE = False
        print("Warning: PyCryptodome not installed. RSA signature will not work.")


class DanaPaymentService:
    """
    DANA Mini Program Payment Service
    """

    def __init__(self):
        self.donationModel = DonationModel()
        self.paymentModel = RefPaymentModel()
        self.campaignModel = RefCampaignModel()
        self.simbaService = SimbaService()
        self.db = Database()

        # DANA Config
        self.merchantId = Config.DANA_MERCHANT_ID
        self.partnerId = Config.DANA_CLIENT_ID

    def logApiCall(self, endpoint, method, requestBody, responseStatus, responseBody,
                   orderId=None, error=None):
        """Log API call ke database"""
        try:
            conn = self.db.getConnection()
            with conn.cursor() as cursor:
                safeRequest = self._maskSensitiveData(requestBody) if requestBody else None
                sql = """
                    INSERT INTO log_api
                    (name, aplikasi, url_api, parameter, response, created_date, created_by, is_active, is_delete)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y', 'N')
                """
                cursor.execute(sql, (
                    f"DANA_PAYMENT_{method}_{orderId or 'unknown'}",
                    'DANA_MINIAPP',
                    endpoint,
                    json.dumps(safeRequest) if safeRequest else None,
                    json.dumps(responseBody) if responseBody else str(error),
                    datetime.now(),
                    'system'
                ))
                conn.commit()
        except Exception as e:
            print(f"Failed to log: {str(e)}")

    def _maskSensitiveData(self, data):
        """Mask sensitive data untuk logging"""
        if not data or not isinstance(data, dict):
            return data
        masked = data.copy()
        for key in ['access_token', 'token']:
            if key in masked and masked[key]:
                masked[key] = '***MASKED***'
        return masked

    def _generateSignature(self, httpMethod, endpointUrl, requestBody, timestamp):
        """
        Generate DANA API signature using RSA Asymmetric Signature (PKCS1_v1_5 + SHA256)
        Sesuai dokumentasi DANA SNAP API

        Format: HTTP_METHOD + ":" + ENDPOINT + ":" + LOWERCASE(HEX(SHA256(minify(REQUEST_BODY)))) + ":" + TIMESTAMP
        """
        try:
            if not CRYPTO_AVAILABLE:
                print("Error: PyCryptodome not installed. Cannot generate RSA signature.")
                print("Install with: pip install pycryptodome")
                return None

            # Get private key from config
            privateKey = Config.DANA_PRIVATE_KEY
            if not privateKey:
                print("Error: DANA_PRIVATE_KEY not configured in .env")
                return None

            # Fix: Handle newline characters from Vercel/Env variables
            if '\\n' in privateKey:
                privateKey = privateKey.replace('\\n', '\n')

            # Format private key to PEM format if needed
            if not privateKey.startswith('-----BEGIN'):
                # Raw base64 key - wrap with PEM headers and format with line breaks
                # PEM format requires 64 characters per line
                keyBody = privateKey.strip()
                # Split into 64-char lines
                lines = [keyBody[i:i+64] for i in range(0, len(keyBody), 64)]
                formattedKey = '\n'.join(lines)
                privateKey = f"-----BEGIN RSA PRIVATE KEY-----\n{formattedKey}\n-----END RSA PRIVATE KEY-----"

            # Minify and hash request body
            bodyStr = json.dumps(requestBody, separators=(',', ':')) if requestBody else ''
            bodyHash = hashlib.sha256(bodyStr.encode('utf-8')).hexdigest().lower()

            # Create string to sign
            stringToSign = f"{httpMethod}:{endpointUrl}:{bodyHash}:{timestamp}"
            print(f"String to sign: {stringToSign}")

            # Load RSA private key
            pkey = RSA.importKey(privateKey)

            # Sign with RSA private key
            signer = PKCS1_v1_5.new(pkey)
            digest = SHA256.new()
            digest.update(stringToSign.encode('utf-8'))
            signature = base64.b64encode(signer.sign(digest)).decode('utf-8')

            print(f"Signature generated: {signature[:50]}...")
            return signature

        except Exception as e:
            print(f"Signature generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _callDanaPaymentApi(self, orderData):
        """
        Call DANA Direct Debit Payment API to create payment order
        Sesuai dokumentasi: /rest/redirection/v1.0/debit/payment-host-to-host

        Returns:
            {
                'success': bool,
                'referenceNo': str,  # tradeNO untuk my.tradePay
                'error': str
            }
        """
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/rest/redirection/v1.0/debit/payment-host-to-host"
            fullUrl = f"{baseUrl}{endpoint}"

            # Generate request timestamp (GMT+7 Jakarta time)
            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')

            # Generate unique X-EXTERNAL-ID (unique per day)
            externalId = f"EXT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

            # Prepare request body sesuai DANA SNAP API Direct Debit Payment
            # Minimal required fields to avoid field format errors
            requestBody = {
                "partnerReferenceNo": orderData['partner_reference_no'],
                "merchantId": Config.DANA_MERCHANT_ID,
                "amount": {
                    "value": f"{orderData['total_bayar']:.2f}",
                    "currency": "IDR"
                },
                "additionalInfo": {
                    "productCode": "51051000100000000001",
                    "order": {
                        "orderTitle": f"Donasi dari {orderData.get('nama_lengkap', 'Hamba Allah')}"[:64]  # Max 64 chars
                    },
                    "mcc": "8398",
                    "envInfo": {
                        "sourcePlatform": "MINIPROGRAM",
                        "terminalType": "APP",
                        "orderTerminalType": "APP"
                    }
                }
            }

            # Generate signature dengan RSA
            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)

            if not signature:
                return {
                    'success': False,
                    'error': 'Failed to generate signature. Check DANA_PRIVATE_KEY configuration.'
                }

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature
            }

            print(f"Calling DANA API: {fullUrl}")
            print(f"Request headers: {json.dumps({k: v for k, v in headers.items() if k != 'X-SIGNATURE'}, indent=2)}")
            print(f"Request body: {json.dumps(requestBody, indent=2)}")

            # Make API call
            response = requests.post(
                fullUrl,
                json=requestBody,
                headers=headers,
                timeout=30
            )

            print(f"DANA API response status: {response.status_code}")
            print(f"DANA API response: {response.text}")

            # Log API call
            try:
                respJson = response.json() if response.ok else None
            except:
                respJson = None

            self.logApiCall(endpoint, 'POST', requestBody, response.status_code,
                           respJson or response.text,
                           orderData['order_id'])

            if response.ok:
                respData = response.json()

                # SNAP API response format:
                # {
                #   "responseCode": "2005400",
                #   "responseMessage": "Successful",
                #   "referenceNo": "2020102977770000000009",
                #   "partnerReferenceNo": "2020102900000000000001",
                #   "webRedirectUrl": "https://...",
                #   "additionalInfo": {}
                # }

                responseCode = respData.get('responseCode')
                responseMessage = respData.get('responseMessage', '')

                # Success codes: 2005400, 2XXXXXX
                if responseCode and responseCode.startswith('2'):
                    # Success - get referenceNo (ini yang dipakai untuk my.tradePay)
                    referenceNo = respData.get('referenceNo')

                    if not referenceNo:
                        print(f"Warning: referenceNo not found in response. Using partnerReferenceNo.")
                        referenceNo = respData.get('partnerReferenceNo') or orderData['partner_reference_no']

                    print(f"✓ DANA API success. referenceNo: {referenceNo}")

                    return {
                        'success': True,
                        'referenceNo': referenceNo,
                        'webRedirectUrl': respData.get('webRedirectUrl'),
                        'danaResponse': respData
                    }
                else:
                    # API returned error
                    errorMsg = f"{responseCode}: {responseMessage}" if responseCode else 'Unknown error'
                    print(f"✗ DANA API error: {errorMsg}")

                    return {
                        'success': False,
                        'error': errorMsg,
                        'danaResponse': respData
                    }
            else:
                errorMsg = f"HTTP {response.status_code}: {response.text}"
                print(f"✗ DANA API HTTP error: {errorMsg}")

                return {
                    'success': False,
                    'error': errorMsg
                }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'DANA API timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Cannot connect to DANA API'}
        except Exception as e:
            print(f"DANA API call failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def createOrder(self, data):
        """
        Create payment order untuk DANA Mini Program

        Args:
            data: {
                nominal: Jumlah donasi
                email: Email donatur
                campaign_id: ID campaign
                nama_lengkap: Nama donatur
                doa_muzaki: Pesan/doa (optional)
                tipe_zakat: 'zakat' atau 'infak'
                hamba_allah: 'Y' atau 'N' (anonymous)
                muzaki_id: ID muzaki (optional)
            }

        Returns:
            {
                orderId: Order ID untuk my.tradePay
                amount: Total amount
                ...
            }
        """
        try:
            # Validate input
            validation = self._validateInput(data)
            if not validation['valid']:
                return Response.error(validation['message'], 400)

            # Prepare order data
            orderData = self._prepareOrderData(data)

            # Try to save to database (with error handling)
            donationId = None
            dbSaved = False
            try:
                donationId = self.donationModel.create(orderData)
                dbSaved = donationId is not None
            except Exception as dbError:
                # Database error - continue with order ID only (for testing)
                print(f"Database save failed (continuing): {str(dbError)}")
                dbSaved = False

            # Call DANA API to create payment order
            # tradeNO untuk my.tradePay harus dari DANA (referenceNo)
            danaApiCalled = False
            tradeNO = orderData['order_id']  # Default to local orderId
            danaReferenceNo = None

            # Check if DANA credentials are configured
            if Config.DANA_CLIENT_ID and Config.DANA_PRIVATE_KEY and Config.DANA_MERCHANT_ID:
                print("Calling DANA Direct Debit Payment API...")
                danaResult = self._callDanaPaymentApi(orderData)

                if danaResult['success']:
                    # Use referenceNo from DANA as tradeNO untuk my.tradePay
                    danaReferenceNo = danaResult['referenceNo']
                    tradeNO = danaReferenceNo
                    danaApiCalled = True
                    print(f"✓ DANA API success, tradeNO: {tradeNO}")

                    # Update database with DANA referenceNo
                    if dbSaved:
                        try:
                            self.donationModel.updateDanaRefs(orderData['order_id'], danaReferenceNo, None)
                        except Exception as dbErr:
                            print(f"Warning: Failed to update DANA refs in DB: {dbErr}")
                else:
                    # DANA API failed - log error
                    print(f"✗ DANA API failed: {danaResult.get('error')}")
                    print("⚠️  Payment popup will NOT work without valid tradeNO from DANA!")
                    print("Check:")
                    print("  1. DANA_PRIVATE_KEY is correct")
                    print("  2. DANA_CLIENT_ID (X-PARTNER-ID) is correct")
                    print("  3. DANA_MERCHANT_ID is correct")
                    print("  4. Network connectivity to DANA sandbox")

                    # Development mode: Allow continuing with local orderId for testing
                    # This enables frontend to test payment flow in simulator
                    dev_mode = os.getenv('DANA_DEV_MODE', 'false').lower() == 'true'
                    if not dev_mode:
                        return Response.error(
                            f"Gagal inisialisasi pembayaran ke DANA: {danaResult.get('error')}",
                            500
                        )
                    else:
                        print("⚠️  DEV MODE: Continuing with local orderId for testing...")
                        tradeNO = orderData['order_id']  # Use local orderId in dev mode
            else:
                print("⚠️  DANA credentials not fully configured!")
                print("Required in .env:")
                print("  - DANA_CLIENT_ID")
                print("  - DANA_PRIVATE_KEY")
                print("  - DANA_MERCHANT_ID")

            try:
                self.logApiCall('/create-order', 'POST', data, 200,
                               {'order_id': orderData['order_id'], 'trade_no': tradeNO, 'dana_api_called': danaApiCalled},
                               orderData['order_id'])
            except:
                pass  # Ignore logging errors

            return Response.success(data={
                "orderId": orderData['order_id'],
                "tradeNO": tradeNO,  # Ini yang dipakai untuk my.tradePay
                "partnerReferenceNo": orderData['partner_reference_no'],
                "amount": int(orderData['total_bayar']),
                "nominal": int(orderData['nominal']),
                "biayaAdmin": int(orderData['biaya_admin']),
                "status": "pending",
                "dbSaved": dbSaved,
                "danaApiCalled": danaApiCalled,
                "message": "Order berhasil dibuat. Gunakan tradeNO untuk my.tradePay()"
            }, message="Order berhasil dibuat")

        except Exception as e:
            return Response.error(f"Create order gagal: {str(e)}", 500)

    def _validateInput(self, data):
        """Validasi input create order"""
        nominal = data.get('nominal')
        if not nominal:
            return {'valid': False, 'message': 'Nominal wajib diisi'}

        try:
            nominal = float(nominal)
            if nominal < 10000:
                return {'valid': False, 'message': 'Minimal donasi Rp 10.000'}
            if nominal > 50000000:
                return {'valid': False, 'message': 'Maksimal donasi Rp 50.000.000'}
        except ValueError:
            return {'valid': False, 'message': 'Nominal tidak valid'}

        if not data.get('email'):
            return {'valid': False, 'message': 'Email wajib diisi'}

        return {'valid': True, 'message': 'OK'}

    def _prepareOrderData(self, data):
        """Siapkan data order untuk database"""
        nominal = float(data.get('nominal'))
        campaignId = data.get('campaign_id')
        metodeId = data.get('metode_id', 2)  # Default DANA

        # Get metode pembayaran DANA (dengan error handling)
        metode = None
        campaign = None

        try:
            if not metodeId:
                metode = self.paymentModel.findByPaymentType('emoney', 'DANA')
                metodeId = metode['id'] if metode else 2
            else:
                metode = self.paymentModel.findById(metodeId)
        except Exception as e:
            print(f"Warning: Could not fetch payment method: {e}")
            metodeId = 2  # Default

        try:
            campaign = self.campaignModel.findById(campaignId) if campaignId else None
        except Exception as e:
            print(f"Warning: Could not fetch campaign: {e}")

        fees = self._calculateFees(nominal, metode, campaign)

        # Generate unique IDs
        orderId = f"DANA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        partnerRef = f"CINTA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

        return {
            'order_id': orderId,
            'partner_reference_no': partnerRef,
            'campaign_id': campaignId,
            'muzaki_id': data.get('muzaki_id'),
            'metode_id': metodeId,
            'nominal': nominal,
            'biaya_admin': fees['admin'],
            'biaya_operasional': fees['ops'],
            'prosen_biayaoperasional': fees['ops_percent'],
            'donasi_net': fees['net'],
            'total_bayar': fees['total'],
            'email': data.get('email'),
            'nama_lengkap': data.get('nama_lengkap', 'Hamba Allah'),
            'doa_muzaki': data.get('doa_muzaki', ''),
            'tipe_zakat': data.get('tipe_zakat', 'infak'),
            'tipe': data.get('tipe', 'perorangan'),
            'hamba_allah': data.get('hamba_allah', 'N'),
            'npwz': data.get('npwz', ''),
            'status': 'pending',
            'created_by': data.get('created_by', 'miniapp')
        }

    def _calculateFees(self, nominal, metode, campaign):
        """Hitung biaya"""
        # Handle None values safely
        opsPercent = 0
        if campaign:
            opsVal = campaign.get('prosen_biayaoperasional')
            if opsVal is not None:
                try:
                    opsPercent = float(opsVal)
                except (TypeError, ValueError):
                    opsPercent = 0

        opsFee = nominal * (opsPercent / 100)

        adminFee = 0
        if metode:
            adminVal = metode.get('biaya_admin')
            if adminVal is not None:
                try:
                    adminRate = float(adminVal)
                    if metode.get('payment_type') == 'emoney':
                        adminFee = adminRate
                    elif 0 < adminRate < 1:
                        adminFee = nominal * adminRate
                    else:
                        adminFee = adminRate
                except (TypeError, ValueError):
                    adminFee = 0

        return {
            'ops': opsFee,
            'ops_percent': opsPercent,
            'admin': adminFee,
            'net': nominal - opsFee,
            'total': nominal + adminFee
        }

    def applyOtt(self, data):
        """
        Apply OTT - Tidak diperlukan untuk Mini Program

        Mini Program menggunakan my.tradePay() yang tidak memerlukan OTT.
        Endpoint ini tetap ada untuk backward compatibility.
        """
        orderId = data.get('order_id')

        if not orderId:
            return Response.error("Order ID wajib diisi", 400)

        donation = self.donationModel.findByOrderId(orderId)
        if not donation:
            return Response.error("Order tidak ditemukan", 404)

        # Return success dengan info order
        return Response.success(data={
            "orderId": orderId,
            "message": "Mini Program tidak memerlukan OTT. Langsung gunakan my.tradePay(tradeNO: orderId)",
            "amount": int(donation.get('total_bayar', 0))
        }, message="Lanjutkan dengan my.tradePay()")

    def queryPayment(self, orderId):
        """Query status pembayaran"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            return Response.success(data={
                "orderId": orderId,
                "status": donation.get('status'),
                "amount": int(donation.get('total_bayar', 0)),
                "nominal": int(donation.get('nominal', 0)),
                "email": donation.get('email'),
                "namaLengkap": donation.get('nama_lengkap'),
                "campaignId": donation.get('campaign_id'),
                "createdAt": str(donation.get('created_date')),
                "paidAt": str(donation.get('paid_date')) if donation.get('paid_date') else None
            }, message="OK")

        except Exception as e:
            return Response.error(f"Query payment gagal: {str(e)}", 500)

    def cancelOrder(self, orderId, reason='User cancelled'):
        """Cancel order yang belum dibayar"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            if donation.get('status') == 'berhasil':
                return Response.error("Order sudah dibayar, tidak bisa dibatalkan", 400)

            self.donationModel.updateStatus(orderId, 'cancelled')

            self.logApiCall('/cancel-order', 'POST', {'order_id': orderId},
                           200, {'status': 'cancelled'}, orderId)

            return Response.success(message="Order berhasil dibatalkan")

        except Exception as e:
            return Response.error(f"Cancel order gagal: {str(e)}", 500)

    def webhook(self, data, signature=None, headers=None):
        """
        Handle webhook dari DANA untuk update status pembayaran
        Sesuai SNAP API standard (Finish Notify)

        DANA akan kirim notifikasi saat:
        - Pembayaran berhasil (SUCCESS)
        - Pembayaran gagal (FAILED)
        - Pembayaran expired (EXPIRED)

        Headers yang dikirim DANA:
        - X-SIGNATURE: Digital signature
        - X-TIMESTAMP: Timestamp request
        """
        try:
            self.logApiCall('/webhook', 'POST', data, 200, None,
                           data.get('merchantTransId') or data.get('partnerReferenceNo') or
                           data.get('originalPartnerReferenceNo'))

            # Extract data dari webhook (support multiple formats)
            # Format 1: Mini App tradePay callback
            # Format 2: SNAP API Finish Notify
            orderId = (data.get('merchantTransId') or
                      data.get('originalPartnerReferenceNo') or
                      data.get('partnerReferenceNo'))
            partnerRef = (data.get('partnerReferenceNo') or
                         data.get('originalPartnerReferenceNo'))
            danaRef = (data.get('referenceNo') or
                      data.get('originalReferenceNo'))
            status = (data.get('status') or
                     data.get('latestTransactionStatus') or
                     data.get('transactionStatus'))

            # Handle amount (bisa object atau string)
            amount = None
            if isinstance(data.get('amount'), dict):
                amount = data.get('amount', {}).get('value')
            else:
                amount = data.get('amount')

            # Log webhook untuk debugging
            try:
                conn = self.db.getConnection()
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO log_dana_webhook
                        (webhook_type, order_id, dana_reference_no, payload, signature, created_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        'FINISH_NOTIFY',
                        orderId,
                        danaRef,
                        json.dumps(data),
                        signature,
                        datetime.now()
                    ))
                    conn.commit()
            except Exception as logErr:
                print(f"Webhook log failed: {str(logErr)}")

            # Cari donation
            donation = None
            if orderId:
                donation = self.donationModel.findByOrderId(orderId)
            if not donation and partnerRef:
                donation = self.donationModel.findByPartnerRefNo(partnerRef)

            if not donation:
                # Return success anyway to acknowledge webhook
                # DANA expects 2xx response
                return {
                    "responseCode": "2005600",
                    "responseMessage": "Successful"
                }, 200

            # Update database dengan DANA status langsung
            # updateDanaStatusRef akan melakukan mapping sendiri
            try:
                # Normalize status untuk database function
                normalizedStatus = status.upper() if status else 'PENDING'
                self.donationModel.updateDanaStatusRef(
                    donation['order_id'],
                    danaRef,
                    normalizedStatus
                )
            except Exception as dbErr:
                print(f"DB update failed: {str(dbErr)}")

            # Map DANA status ke internal status untuk sync ke SIMBA
            internalStatus = self._mapDanaStatus(status)

            # Sync ke SIMBA jika sukses
            if internalStatus == 'berhasil':
                self._syncToSimba(donation)

            # Response sesuai format DANA SNAP API
            return {
                "responseCode": "2005600",
                "responseMessage": "Successful"
            }, 200

        except Exception as e:
            self.logApiCall('/webhook', 'POST', data, 500, None, error=str(e))
            # Still return success to DANA to avoid retries
            return {
                "responseCode": "2005600",
                "responseMessage": "Successful"
            }, 200

    def _mapDanaStatus(self, danaStatus):
        """Map DANA status ke internal status"""
        if not danaStatus:
            return 'pending'

        statusMap = {
            'SUCCESS': 'berhasil',
            'PAID': 'berhasil',
            'COMPLETED': 'berhasil',
            'FAILED': 'gagal',
            'CANCELLED': 'dibatalkan',
            'EXPIRED': 'expired',
            'PENDING': 'pending',
            'INIT': 'pending'
        }
        return statusMap.get(danaStatus.upper(), 'pending')

    def _syncToSimba(self, donation):
        """Sync transaksi ke SIMBA setelah sukses"""
        try:
            donation = self.donationModel.findByOrderId(donation['order_id'])

            if not donation.get('npwz'):
                npwz = self.simbaService.register_muzaki(donation, None)
                if npwz:
                    self.donationModel.updateNpwz(donation['order_id'], npwz)
                    donation['npwz'] = npwz

            self.simbaService.save_transaction(donation)

        except Exception as e:
            print(f"SIMBA sync failed: {str(e)}")

    def finishPayment(self, data):
        """
        Handle finish payment callback dari DANA atau mini app

        Endpoint ini dipanggil setelah user selesai pembayaran:
        - Dari DANA redirect callback
        - Dari mini app setelah my.tradePay success
        - Dari dev_mode simulation
        """
        orderId = data.get('orderId') or data.get('merchantTransId')
        resultCode = data.get('resultCode')
        resultStatus = data.get('resultStatus')
        devMode = data.get('dev_mode', False)

        if not orderId:
            return Response.success(data={
                "message": "Callback received",
                "resultCode": resultCode
            })

        # Map result code to status
        if resultCode == '9000':
            status = 'berhasil'
        elif resultCode == '6001':
            status = 'dibatalkan'
        else:
            status = 'pending'

        # Try to update database
        dbUpdated = False
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if donation:
                # Update status in database
                if status == 'berhasil':
                    self.donationModel.updateDanaStatusRef(orderId, f"DEV-{orderId}" if devMode else orderId, status)
                    dbUpdated = True

                    # Log the payment completion
                    self.logApiCall('/finish-payment', 'POST',
                                   {'orderId': orderId, 'resultCode': resultCode, 'devMode': devMode},
                                   200, {'status': status}, orderId)
        except Exception as e:
            print(f"Database update failed: {str(e)}")
            dbUpdated = False

        return Response.success(data={
            "orderId": orderId,
            "status": status,
            "resultCode": resultCode,
            "dbUpdated": dbUpdated,
            "devMode": devMode,
            "message": "Payment callback received"
        })
