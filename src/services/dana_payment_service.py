"""
DANA Mini Program Payment Service
Untuk integrasi pembayaran di DANA Mini App (Partner Webview Onboarding)

Flow Mini Program Payment (Partner Webview Onboarding):
1. User isi form donasi di mini app
2. Mini app call backend /create-order
3. Backend call DANA Direct Debit Payment API -> dapat webRedirectUrl (checkoutUrl)
4. Backend return checkoutUrl ke mini app
5. Mini app call my.tradePay({ paymentUrl: checkoutUrl })
6. DANA SDK handle pembayaran (popup PIN muncul)
7. DANA kirim Finish Notify webhook ke backend untuk update status

API Reference:
- Endpoint: /rest/redirection/v1.0/debit/payment-host-to-host
- Signature: RSA asymmetric (PKCS1_v1_5 + SHA256)
- Response: webRedirectUrl digunakan sebagai paymentUrl untuk my.tradePay
"""

from src.models.donation_model import DonationModel
from src.models.user_model import UserModel
from src.models.master_models import RefPaymentModel, RefCampaignModel
from src.models.log_dana_transaction_model import LogDanaTransactionModel
from src.services.simba_service import SimbaService
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime, timezone, timedelta
import os
import uuid
from random import randint
import json
import requests
import hashlib
import base64
import hmac
import logging

# Setup logging
logger = logging.getLogger(__name__)

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
        self.userModel = UserModel()
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
                'referenceNo': str,
                'checkoutUrl': str,  # webRedirectUrl untuk my.tradePay({ paymentUrl })
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
            # Sesuai Partner Webview Onboarding: tambah mcc (required), productCode, envInfo
            requestBody = {
                "partnerReferenceNo": orderData['partner_reference_no'],
                "merchantId": Config.DANA_MERCHANT_ID,
                "productCode": "51051000100000000001",
                "amount": {
                    "value": f"{orderData['total_bayar']:.2f}",
                    "currency": "IDR"
                },
                "validUpTo": (datetime.now(timezone(timedelta(hours=7))) + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S+07:00'),
                "urlParams": [
                    {
                        "url": f"{Config.API_BASE_URL}/api/v1/dana/webhook",
                        "type": "NOTIFICATION",
                        "isDeeplink": "N"
                    }
                ],
                "additionalInfo": {
                    "mcc": "8398",  # Required
                    "productCode": "51051000100000000001",
                    "order": {
                        "orderTitle": f"Donasi dari {orderData.get('nama_lengkap', 'Hamba Allah')}"[:64]
                    },
                    "envInfo": {
                        "sourcePlatform": Config.DANA_SOURCE_PLATFORM,
                        "terminalType": Config.DANA_TERMINAL_TYPE,
                        "orderTerminalType": Config.DANA_ORDER_TERMINAL_TYPE
                    }
                }
            }
            
            # Conditionally add optional fields
            if orderData.get('payer_phone'):
                requestBody['additionalInfo']['phoneNumber'] = orderData['payer_phone']
            
            if orderData.get('payer_dana_id'):
                requestBody['additionalInfo']['publicUserId'] = orderData['payer_dana_id']

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

                    checkoutUrl = respData.get('webRedirectUrl')
                    print(f"✓ DANA API success. referenceNo: {referenceNo}, checkoutUrl: {checkoutUrl}")

                    return {
                        'success': True,
                        'referenceNo': referenceNo,
                        'checkoutUrl': checkoutUrl,  # webRedirectUrl untuk my.tradePay({ paymentUrl })
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

            # Email update tracking
            emailUpdated = False
            userEmailUpdated = None

            # Enrich with User Data if logged in
            createdBy = orderData.get('created_by', '')
            if createdBy and createdBy.startswith('user_'):
                try:
                    userId = createdBy.split('_')[1]
                    
                    # Use fresh UserModel instance to avoid transaction conflicts
                    localUserModel = UserModel()
                    try:
                        user = localUserModel.findById(userId)
                        print(f"[PAYMENT] createOrder user found: {user.get('id') if user else 'None'}")
                        if user:
                            # Auto-update user email if empty
                            userEmail = user.get('email')
                            inputEmail = data.get('email')
                            print(f"[PAYMENT] Email check - User: '{userEmail}', Input: '{inputEmail}'")
                            
                            if (not userEmail or userEmail == '') and inputEmail:
                                try:
                                    print(f"[PAYMENT] Updating user {userId} email from empty to {inputEmail}")
                                    localUserModel.updateEmail(userId, inputEmail)
                                    emailUpdated = True
                                    userEmailUpdated = inputEmail
                                    print(f"[PAYMENT] Email update success flag set")
                                except Exception as emailErr:
                                    print(f"[PAYMENT] Failed to update user email: {emailErr}")
                            else:
                                print(f"[PAYMENT] Skip email update. Condition not met.")
                                # Send existing email to frontend for sync
                                if userEmail and userEmail != '':
                                    userEmailUpdated = userEmail
                                    print(f"[PAYMENT] Sending existing email to frontend: {userEmail}")
    
                            # Add DANA specific user info
                            orderData['payer_phone'] = user.get('handphone') or user.get('no_hp')
                            orderData['payer_dana_id'] = user.get('dana_user_id') or user.get('dana_external_id')
                            print(f"Enriched order with user data: {userId}, Phone: {orderData.get('payer_phone')}")
                    finally:
                        # Close local connection to prevent leaks
                        try:
                            if hasattr(localUserModel, 'conn') and localUserModel.conn:
                                localUserModel.conn.close()
                        except:
                            pass
                except Exception as e:
                    print(f"Failed to fetch user data for order: {e}")

            # Fallback: Get phone from input data if not found in User DB
            if not orderData.get('payer_phone') and data.get('phone'):
                orderData['payer_phone'] = data.get('phone')
            
            # Format phone number if exists (remove 62- prefix, ensure 08...)
            if orderData.get('payer_phone'):
                phone = str(orderData['payer_phone'])
                if phone.startswith('62-'):
                    phone = '0' + phone[3:]
                elif phone.startswith('62'):
                    phone = '0' + phone[2:]
                orderData['payer_phone'] = phone

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

            checkoutUrl = None

            # Check if DANA credentials are configured
            if Config.DANA_CLIENT_ID and Config.DANA_PRIVATE_KEY and Config.DANA_MERCHANT_ID:
                print("Calling DANA Direct Debit Payment API...")
                danaResult = self._callDanaPaymentApi(orderData)

                if danaResult['success']:
                    danaReferenceNo = danaResult['referenceNo']
                    checkoutUrl = danaResult.get('checkoutUrl')  # webRedirectUrl untuk my.tradePay
                    tradeNO = danaReferenceNo
                    danaApiCalled = True
                    print(f"✓ DANA API success, referenceNo: {tradeNO}, checkoutUrl: {checkoutUrl}")

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

            # Log transaction to log_dana_transaction table
            try:
                logModel = LogDanaTransactionModel()
                logModel.create({
                    'order_id': orderData['order_id'],
                    'partner_reference_no': orderData['partner_reference_no'],
                    'merchant_id': Config.DANA_MERCHANT_ID,
                    'amount': orderData['total_bayar'],
                    'currency': 'IDR',
                    'status': 'PENDING',
                    'status_desc': 'Order created, awaiting payment',
                    'user_id': orderData.get('created_by', '').replace('user_', '') if orderData.get('created_by', '').startswith('user_') else None,
                    'email': orderData.get('email', ''),
                    'phone': orderData.get('handphone', ''),
                    'raw_payload': {
                        'order_data': orderData,
                        'trade_no': tradeNO,
                        'checkout_url': checkoutUrl
                    }
                })
            except Exception as logErr:
                print(f"[LOG_DANA] Failed to log transaction: {logErr}")

            return Response.success(data={
                "orderId": orderData['order_id'],
                "tradeNO": tradeNO,
                "checkoutUrl": checkoutUrl,  # webRedirectUrl untuk my.tradePay({ paymentUrl })
                "partnerReferenceNo": orderData['partner_reference_no'],
                "amount": int(orderData['total_bayar']),
                "nominal": int(orderData['nominal']),
                "biayaAdmin": int(orderData['biaya_admin']),
                "status": "pending",
                "dbSaved": dbSaved,
                "danaApiCalled": danaApiCalled,
                "emailUpdated": emailUpdated,
                "userEmail": userEmailUpdated,
                "message": "Order berhasil dibuat. Gunakan checkoutUrl untuk my.tradePay({ paymentUrl })"
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
        # Handle Mini App payload keys mismatch
        nominal = data.get('nominal')
        if not nominal:
            nominal = data.get('amount')
        
        nominal = float(nominal) if nominal else 0
            
        campaignId = data.get('campaign_id')
        if not campaignId:
            campaignId = data.get('campaignId')
            
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

        # Map optional fields
        nama_lengkap = data.get('nama_lengkap') or data.get('donorName')
        if not nama_lengkap:
            nama_lengkap = 'Hamba Allah'
            
        hamba_allah = data.get('hamba_allah')
        if hamba_allah is None:
            is_anon = data.get('isAnonymous')
            if is_anon is not None:
                hamba_allah = 'Y' if str(is_anon).lower() in ['true', '1', 'y', 'yes'] else 'N'
            else:
                hamba_allah = 'N'
                
        doa = data.get('doa_muzaki') or data.get('message', '')
        tipe_zakat = data.get('tipe_zakat') or ('zakat' if data.get('isZakat') else 'infak')

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
            'nama_lengkap': nama_lengkap,
            'doa_muzaki': doa,
            'tipe_zakat': tipe_zakat,
            'tipe': data.get('tipe', 'perorangan'),
            'hamba_allah': hamba_allah,
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

    def _callDanaQueryPaymentApi(self, orderId):
        """
        Call DANA Query Payment API (SNAP API)
        Sesuai dokumentasi: /rest/v1.1/debit/status
        """
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/rest/v1.1/debit/status"
            fullUrl = f"{baseUrl}{endpoint}"

            # Generate request timestamp
            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')

            # Generate unique X-EXTERNAL-ID
            externalId = f"EXT-QUERY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

            # Get donation to find correct references
            donation = self.donationModel.findByOrderId(orderId)
            partnerRef = orderId
            danaRef = None
            if donation:
                partnerRef = donation.get('partner_reference_no') or orderId
                danaRef = donation.get('dana_reference_no')

            # Request Body
            requestBody = {
                "merchantId": Config.DANA_MERCHANT_ID,
                "originalPartnerReferenceNo": partnerRef,
                "serviceCode": "51", # Default to 51 (Direct Debit)
                "amount": {
                   "value": "0.00", # Value is ignored for query usually, but required by schema?
                   "currency": "IDR"
                },
                "additionalInfo": {}
            }
            if danaRef:
                requestBody['originalReferenceNo'] = danaRef

            # Generate signature
            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            if not signature:
                return {'success': False, 'error': 'Failed to generate signature'}

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature
            }

            print(f"Calling DANA Query API: {fullUrl}")
            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            
            print(f"DANA Query response: {response.status_code} {response.text}")

            self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                            response.json() if response.ok else response.text, orderId)

            if response.ok:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            print(f"DANA Query API failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def queryPayment(self, orderId):
        """Query status pembayaran (Local DB + DANA API)"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            # Jika status masih pending, coba cek ke DANA
            currentStatus = donation.get('status')
            if currentStatus == 'pending':
                print(f"Order {orderId} is pending. Checking with DANA...")
                danaResult = self._callDanaQueryPaymentApi(orderId)
                
                if danaResult['success']:
                    danaData = danaResult['data']
                    latestStatus = danaData.get('latestTransactionStatus')
                    
                    # Map DANA status to internal status
                    newStatus = self._mapDanaStatus(latestStatus)
                    
                    if newStatus and newStatus != 'pending':
                        print(f"Updating status from pending to {newStatus}")
                        # Update DB
                        try:
                            danaRef = danaData.get('originalReferenceNo') or danaData.get('referenceNo')
                            self.donationModel.updateDanaStatusRef(orderId, danaRef, latestStatus) # This updates local status too
                            
                            # Refresh donation data
                            donation = self.donationModel.findByOrderId(orderId)
                            
                            # Sync to SIMBA if success
                            if newStatus == 'berhasil':
                                self._syncToSimba(donation)
                                
                        except Exception as dbErr:
                            print(f"Failed to update status from query result: {dbErr}")

            return Response.success(data={
                "orderId": orderId,
                "status": donation.get('status'),
                "amount": int(donation.get('total_bayar', 0)),
                "nominal": int(donation.get('nominal', 0)),
                "email": donation.get('email'),
                "namaLengkap": donation.get('nama_lengkap'),
                "campaignId": donation.get('campaign_id'),
                "createdAt": str(donation.get('created_date')),
                "paidAt": str(donation.get('paid_date')) if donation.get('paid_date') else None,
                "danaStatus": donation.get('dana_status') # Tambahan info
            }, message="OK")

        except Exception as e:
            return Response.error(f"Query payment gagal: {str(e)}", 500)

    def _callDanaCancelApi(self, orderId, reason):
        """Call DANA Cancel Order API"""
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/debit/cancel.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            timestamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            externalId = f"EXT-CANCEL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"

            requestBody = {
                "merchantId": Config.DANA_MERCHANT_ID,
                "originalPartnerReferenceNo": orderId,
                "reason": reason[:256],
                "amount": { "value": "0.00", "currency": "IDR" }, # Amount ignored/not strictly required for cancel usually, checking schema
                "additionalInfo": {}
            }
            # Note: Docs say "amount" is in body. Some SNAP impls require it, some don't for cancel. 
            # We will fetch amount from DB to be safe if strictly required, but usually cancel is by OrderID.
            # Let's fetch donation to fill amount if needed.
            donation = self.donationModel.findByOrderId(orderId)
            if donation:
                requestBody['amount']['value'] = f"{int(donation.get('total_bayar', 0)):.2f}"

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature
            }

            print(f"Calling DANA Cancel API: {fullUrl}")
            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                            response.json() if response.ok else response.text, orderId)
            
            if response.ok:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cancelOrder(self, orderId, reason='User cancelled'):
        """Cancel order yang belum dibayar (Local + API)"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            if donation.get('status') == 'berhasil':
                return Response.error("Order sudah dibayar, tidak bisa dibatalkan", 400)

            # Call DANA API first
            danaResult = self._callDanaCancelApi(orderId, reason)
            
            # Even if DANA API fails (e.g. order not found in DANA), we might want to cancel locally?
            # But strictly, if DANA says "success" or "not found", we can cancel.
            # For now, we process local cancel execution.
            
            self.donationModel.updateStatus(orderId, 'cancelled')
            
            # Log result
            apiStatus = "Success" if danaResult.get('success') else f"Failed: {danaResult.get('error')}"
            print(f"Cancel Order result: Local=Success, DANA={apiStatus}")

            return Response.success(data={'dana_cancel': danaResult}, message="Order berhasil dibatalkan")

        except Exception as e:
            return Response.error(f"Cancel order gagal: {str(e)}", 500)

    def _callDanaRefundApi(self, orderId, amount, reason):
        """Call DANA Refund Order API"""
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/debit/refund.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            timestamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            externalId = f"EXT-REFUND-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            partnerRefundNo = f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{randint(1000,9999)}"

            requestBody = {
                "merchantId": Config.DANA_MERCHANT_ID,
                "originalPartnerReferenceNo": orderId,
                "partnerRefundNo": partnerRefundNo,
                "refundAmount": {
                    "value": f"{amount:.2f}",
                    "currency": "IDR"
                },
                "reason": reason[:256],
                "additionalInfo": {}
            }

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature
            }

            print(f"Calling DANA Refund API: {fullUrl}")
            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                            response.json() if response.ok else response.text, orderId)

            if response.ok:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def refundOrder(self, orderId, reason='Admin refund'):
        """Refund order yang sudah berhasil"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)
            
            if donation.get('status') != 'berhasil':
                return Response.error("Hanya order berhasil yang bisa di-refund", 400)

            amount = float(donation.get('total_bayar', 0))
            
            # Call DANA API
            result = self._callDanaRefundApi(orderId, amount, reason)
            
            if result['success']:
                # Update status locally
                # Assuming we reuse 'dibatalkan' or have 'refunded' status. 
                # Since 'refunded' might not exist in ENUM, we use 'dibatalkan' or just update dana_status.
                # Let's try to update dana_status mostly.
                try:
                    self.donationModel.updateDanaStatusRef(orderId, donation.get('dana_reference_no'), 'REFUNDED')
                except:
                    pass
                return Response.success(data=result['data'], message="Refund berhasil diproses")
            else:
                return Response.error(f"Refund gagal: {result.get('error')}", 500)

        except Exception as e:
            return Response.error(f"Refund exception: {str(e)}", 500)

    def _callDanaBalanceInquiryApi(self, accessToken):
        """Call DANA Balance Inquiry API"""
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/balance-inquiry.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            timestamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            externalId = f"EXT-BAL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            # Partner Ref No can be anything unique
            partnerRef = f"BAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            requestBody = {
                "partnerReferenceNo": partnerRef,
                "balanceTypes": ["BALANCE"],
                "additionalInfo": {
                    "accessToken": accessToken
                }
            }

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'X-DEVICE-ID': 'BACKEND-SERVER', # Generic device ID
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature,
                'Authorization-Customer': f"Bearer {accessToken}" # Also required in header sometimes? Specs say header Authorization-Customer OR additionalInfo.accessToken. Lets do both/header.
            }
            # Spec says "Authorization-Customer" header required.

            print(f"Calling DANA Balance Inquiry API: {fullUrl}")
            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=10)
            self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                            response.json() if response.ok else response.text, partnerRef)

            if response.ok:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f"{response.status_code}: {response.text}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def balanceInquiry(self, userId):
        """Cek saldo DANA user (Need Account Binding)"""
        try:
            # Get Access Token from User Table (saved during binding/seamless login)
            user = self.userModel.findById(userId)
            if not user:
                return Response.error("User not found", 404)
            
            accessToken = user.get('dana_access_token')
            if not accessToken:
                return Response.error("User belum terhubung dengan DANA (Access Token missing)", 400)

            result = self._callDanaBalanceInquiryApi(accessToken)
            
            if result['success']:
                return Response.success(data=result['data'], message="Balance inquiry success")
            else:
                return Response.error(f"Gagal cek saldo: {result.get('error')}", 500)

        except Exception as e:
            return Response.error(f"Balance inquiry error: {str(e)}", 500)

    def _callDanaTransactionHistoryApi(self, accessToken, page=1, pageSize=10, fromDate=None, toDate=None):
        """Call DANA Transaction History API"""
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/transaction-history-list.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            timestamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            externalId = f"EXT-HIST-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            partnerRef = f"HIST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Default dates if not provided (Last 1 month)
            if not toDate:
                toDate = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            if not fromDate:
                fromDate = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')

            requestBody = {
                "partnerReferenceNo": partnerRef,
                "fromDateTime": fromDate,
                "toDateTime": toDate,
                "pageSize": str(pageSize),
                "pageNumber": str(page),
                "additionalInfo": {
                    "accessToken": accessToken,
                    "types": ["PAYMENT", "REFUND", "TOP_UP"], # Adjust types as needed
                    "statuses": ["SUCCESS", "PROCESSING", "FAILED", "CLOSED"]
                }
            }

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': externalId,
                'X-DEVICE-ID': 'BACKEND-SERVER',
                'X-IP-ADDRESS': '127.0.0.1', # Dummy or Real IP
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature,
                'Authorization-Customer': f"Bearer {accessToken}" # Spec requirements
            }

            print(f"Calling DANA History API: {fullUrl}")
            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                            response.json() if response.ok else response.text, partnerRef)

            if response.ok:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def transactionHistory(self, userId, page=1, pageSize=10):
        """
        Get user transaction history

        Strategy:
        1. Try to get from DANA API if user has access token
        2. Fallback to local database (log_dana_transaction table)
        """
        try:
            logger.info(f"[HISTORY] Starting transaction history retrieval - userId={userId}, page={page}, pageSize={pageSize}")
            
            user = self.userModel.findById(userId)
            if not user:
                logger.warning(f"[HISTORY] User not found for ID {userId}")
                return Response.error("User not found", 404)

            email = user.get('email')
            accessToken = user.get('dana_access_token')
            logger.info(f"[HISTORY] User found. Email={email}, AccessToken={'Yes' if accessToken else 'No'}")

            # Try DANA API first if user has access token
            if accessToken:
                logger.info(f"[HISTORY] Attempting DANA API...")
                result = self._callDanaTransactionHistoryApi(accessToken, page, pageSize)

                if result['success']:
                    logger.info(f"[HISTORY] ✅ DANA API SUCCESS - Returning DANA API data")
                    return Response.success(data=result['data'], message="History retrieved from DANA")
                else:
                    logger.warning(f"[HISTORY] DANA API FAILED: {result.get('error')}")
                    logger.info(f"[HISTORY] Falling back to local database...")
            else:
                logger.info(f"[HISTORY] No access token, using local database")

            # Fallback to local database
            logger.info(f"[HISTORY] Querying local database...")
            logModel = LogDanaTransactionModel()
            transactions = logModel.getByUserId(userId, page, pageSize)

            # If no transactions by userId, try by email
            if not transactions and email:
                logger.info(f"[HISTORY] No transactions by userId, trying email...")
                transactions = logModel.getByEmail(email, page, pageSize)

            logger.info(f"[HISTORY] Found {len(transactions)} transactions in local DB")
            
            # Debug: Print first record to see what fields are available
            if transactions and len(transactions) > 0:
                logger.debug(f"[HISTORY] First record keys: {list(transactions[0].keys())}")
                logger.debug(f"[HISTORY] First record raw data: {json.dumps({k: str(v) for k, v in transactions[0].items()}, default=str)}")

            # Format response similar to DANA API format
            formatted_data = {
                "responseCode": "2001200",
                "responseMessage": "Success (from local database)",
                "detailData": []
            }

            for idx, tx in enumerate(transactions):
                # Determine transaction date/time from correct database fields
                trans_dt = None
                tgl_str = None
                waktu_str = None
                
                # Get the values
                tanggal = tx.get('tanggal')
                waktu = tx.get('waktu')
                tgl_donasi = tx.get('tgl_donasi')
                created_date = tx.get('created_date')
                
                logger.debug(f"[HISTORY] Tx {idx}: tanggal={tanggal}, waktu={waktu}, tgl_donasi={tgl_donasi}, created_date={created_date}")
                
                # Priority 1: Use tanggal + waktu (VARCHAR fields from DANA response)
                if tanggal and waktu:
                    try:
                        tanggal_str = str(tanggal).strip()
                        waktu_str = str(waktu).strip()
                        tgl_str = tanggal_str
                        
                        # Try to parse and combine
                        # Common formats: "DD-MM-YYYY HH:MM:SS", "YYYY-MM-DD HH:MM:SS"
                        for date_format in ['%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d-%m-%Y', '%Y-%m-%d']:
                            try:
                                combined_str = f"{tanggal_str} {waktu_str}".strip()
                                trans_dt = datetime.strptime(combined_str, date_format.replace('%S', '%S'))
                                logger.debug(f"[HISTORY] Parsed tanggal+waktu as {date_format}")
                                break
                            except ValueError:
                                continue
                        
                        # If parsing failed, try time separately
                        if not trans_dt and waktu_str:
                            for time_format in ['%H:%M:%S', '%H:%M']:
                                try:
                                    time_obj = datetime.strptime(waktu_str, time_format).time()
                                    date_obj = datetime.strptime(tanggal_str, '%d-%m-%Y').date() if '-' in tanggal_str and len(tanggal_str.split('-')[0]) <= 2 else datetime.strptime(tanggal_str, '%Y-%m-%d').date()
                                    trans_dt = datetime.combine(date_obj, time_obj)
                                    logger.debug(f"[HISTORY] Parsed tanggal+waktu separately")
                                    break
                                except ValueError:
                                    continue
                    except Exception as e:
                        logger.warning(f"[HISTORY] Failed to parse tanggal+waktu: {e}")
                
                # Priority 2: Use tgl_donasi (DATE field)
                if not trans_dt and tgl_donasi:
                    try:
                        tgl_donasi_val = tgl_donasi
                        tgl_str = str(tgl_donasi_val)
                        if isinstance(tgl_donasi_val, str):
                            trans_dt = datetime.strptime(tgl_donasi_val, '%Y-%m-%d').replace(hour=12, minute=0, second=0)
                        else:
                            # Assume it's a date object
                            trans_dt = datetime.combine(tgl_donasi_val, datetime.min.time())
                        logger.debug(f"[HISTORY] Using tgl_donasi: {tgl_str}")
                    except Exception as e:
                        logger.warning(f"[HISTORY] Failed to parse tgl_donasi: {e}")
                
                # Priority 3: Use created_date (TIMESTAMP field)
                if not trans_dt and created_date:
                    try:
                        created_date_val = created_date
                        tgl_str = str(created_date_val)
                        if isinstance(created_date_val, str):
                            # Try common timestamp formats
                            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                                try:
                                    trans_dt = datetime.strptime(created_date_val[:19], fmt[:19])
                                    logger.debug(f"[HISTORY] Using created_date: {tgl_str}")
                                    break
                                except ValueError:
                                    continue
                        else:
                            trans_dt = created_date_val
                            logger.debug(f"[HISTORY] Using created_date (object): {tgl_str}")
                    except Exception as e:
                        logger.warning(f"[HISTORY] Failed to parse created_date: {e}")

                formatted_data["detailData"].append({
                    "originalPartnerReferenceNo": tx.get('partner_reference_no') or tx.get('order_id'),
                    "originalReferenceNo": tx.get('dana_reference_no') or tx.get('order_id'),
                    "transDateTime": trans_dt.isoformat() if trans_dt else None,
                    "transDate": tgl_str,  # Original date string (separate field)
                    "transTime": waktu_str or (trans_dt.strftime('%H:%M:%S') if trans_dt else None),  # Time component
                    "amount": {
                        "value": str(tx.get('amount', 0)),
                        "currency": tx.get('currency', 'IDR')
                    },
                    "transactionStatus": tx.get('status'),
                    "transactionStatusDesc": tx.get('status_desc'),
                    "merchantId": tx.get('merchant_id'),
                    "paymentMethod": tx.get('payment_method'),
                    "campaignName": tx.get('campaign_name'),
                    "campaignKategori": tx.get('campaign_kategori'),
                    "institutionName": tx.get('institution_name'),
                    "source": "local_database"
                })

            logger.info(f"[HISTORY] ✅ API HIT SUCCESS - Formatted {len(formatted_data['detailData'])} transactions")
            logger.info(f"[HISTORY] Response sample: {json.dumps(formatted_data['detailData'][0] if formatted_data['detailData'] else {}, default=str)[:500]}...")
            
            return Response.success(
                data=formatted_data,
                message=f"History retrieved from local database ({len(transactions)} transactions)"
            )

        except Exception as e:
            import traceback
            errorMsg = traceback.format_exc()
            logger.error(f"[HISTORY] ❌ EXCEPTION: {errorMsg}")
            return Response.error(f"History error: {str(e)}", 500)

    def _callDanaTransactionDetailApi(self, accessToken, danaRefNo):
        """Call DANA Transaction Detail API"""
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/transaction-history-detail.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            timestamp = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            externalId = f"EXT-DETAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Look up partnerRef and danaRef in DB first
            transaction_db = None
            partnerReferenceNo = None
            danaRefNo = None
            
            # Helper to find donation
            try:
                # 1. Try as Partner Ref (CINTA-...) - Most likely from frontend
                transaction_db = self.donationModel.findByPartnerRefNo(danaRefNo)
                
                # 2. Try as Order ID (DANA-...)
                if not transaction_db:
                    transaction_db = self.donationModel.findByOrderId(danaRefNo)

                # 3. Try as DANA Ref (Numeric)
                if not transaction_db:
                     with self.donationModel.conn.cursor() as cursor:
                        cursor.execute(f"SELECT * FROM {self.donationModel.table_name} WHERE dana_reference_no = %s LIMIT 1", (danaRefNo,))
                        transaction_db = cursor.fetchone()

                if transaction_db:
                    partnerReferenceNo = transaction_db.get('partner_reference_no') or transaction_db.get('order_id')
                    danaRefNo = transaction_db.get('dana_reference_no')

            except Exception as e:
                print(f"[DETAIL] Failed to lookup refs: {e}")

            # If we found DB record and have danaRef, call API. 
            # If we don't have danaRef (e.g. pending local), we can't call API Detail (requires danaRef).
            if accessToken and danaRefNo and partnerReferenceNo:
                requestBody = {
                    "originalPartnerReferenceNo": partnerReferenceNo, 
                    "additionalInfo": {
                        "accessToken": accessToken,
                        "referenceNo": danaRefNo
                    }
                }
                
                signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
                headers = {
                    'Content-Type': 'application/json',
                    'X-TIMESTAMP': timestamp,
                    'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                    'X-EXTERNAL-ID': externalId,
                    'X-DEVICE-ID': 'BACKEND-SERVER',
                    'X-IP-ADDRESS': '127.0.0.1',
                    'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                    'X-SIGNATURE': signature,
                    'Authorization-Customer': f"Bearer {accessToken}"
                }

                print(f"Calling DANA Detail API: {fullUrl}")
                response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
                self.logApiCall(endpoint, 'POST', requestBody, response.status_code, 
                                response.json() if response.ok else response.text, danaRefNo)

                if response.ok:
                    return {'success': True, 'data': response.json()}
                return {'success': False, 'error': f"{response.status_code}: {response.text}"}
            else:
                 # Force fallback if we can't construct valid API request
                 return {'success': False, 'error': "Missing DANA Ref or Partner Ref"}

            if response.ok:
                return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def transactionDetail(self, userId, refNo):
        """
        Get transaction detail

        Strategy:
        1. Try DANA API if user has access token
        2. Fallback to local database by refNo (dana_reference_no or order_id)
        """
        try:
            print(f"[DETAIL] Finding user {userId}, refNo={refNo}")
            user = self.userModel.findById(userId)
            if not user:
                return Response.error("User not found", 404)

            accessToken = user.get('dana_access_token')

            # Try DANA API first if user has access token
            if accessToken:
                print(f"[DETAIL] Attempting DANA API...")
                result = self._callDanaTransactionDetailApi(accessToken, refNo)

                if result['success']:
                    print(f"[DETAIL] DANA API SUCCESS")
                    return Response.success(data=result['data'], message="Detail retrieved from DANA")
                else:
                    print(f"[DETAIL] DANA API FAILED: {result.get('error')}")
                    print(f"[DETAIL] Falling back to local database...")
            else:
                print(f"[DETAIL] No access token, using local database")

            # Fallback to local database
            logModel = LogDanaTransactionModel()

            # Try to find by dana_reference_no or order_id (with campaign info)
            transaction = None

            # Query with JOIN to get campaign and institution info
            # Query with JOIN to get campaign and institution info
            try:
                with logModel.conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT
                            t.*,
                            d.campaign_id,
                            c.name as campaign_name,
                            c.kategori as campaign_kategori,
                            k.name as institution_name,
                            k.kode_institusi
                        FROM {logModel.table_name} t
                        LEFT JOIN adm_campaign_donasi d ON t.order_id = d.order_id
                        LEFT JOIN adm_campaign c ON d.campaign_id = c.id
                        LEFT JOIN ref_kantor k ON c.kode_institusi = k.id
                        WHERE t.dana_reference_no = %s OR t.order_id = %s
                        ORDER BY t.webhook_received_at DESC
                        LIMIT 1
                    """, (refNo, refNo))
                    transaction = cursor.fetchone()
            except Exception as e:
                print(f"[DETAIL] Failed to query log table: {str(e)}")
                try:
                    logModel.conn.rollback()
                except:
                    pass
                transaction = None

            # Fallback: Query adm_campaign_donasi directly if not found in log
            if not transaction:
                print(f"[DETAIL] Not found in log, searching adm_campaign_donasi...")
                with logModel.conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            d.order_id, d.partner_reference_no, d.dana_reference_no, d.status, 
                            d.nominal as amount, d.tgl_donasi as created_time, 
                            d.dana_paid_at as paid_time,
                            d.campaign_id, 
                            'DANA' as payment_method,
                            c.name as campaign_name, c.kategori as campaign_kategori,
                            k.name as institution_name, k.kode_institusi,
                            'adm_campaign_donasi' as source_table
                        FROM adm_campaign_donasi d
                        LEFT JOIN adm_campaign c ON d.campaign_id = c.id
                        LEFT JOIN ref_kantor k ON c.kode_institusi = k.id
                        WHERE d.dana_reference_no = %s OR d.order_id = %s OR d.partner_reference_no = %s
                        LIMIT 1
                    """, (refNo, refNo, refNo))
                    transaction = cursor.fetchone()
            if not transaction:
                print(f"[DETAIL] Transaction not found in local DB")
                return Response.error("Transaction not found", 404)

            print(f"[DETAIL] Found transaction in local DB: {transaction.get('order_id')}")

            # Format response similar to DANA API format
            status_mapping = {
                'berhasil': 'SUCCESS',
                'pending': 'PENDING',
                'belum': 'PENDING',
                'menunggu': 'PENDING',
                'gagal': 'FAILED',
                'dibatalkan': 'FAILED'
            }
            db_status = transaction.get('status', '').lower()
            api_status = status_mapping.get(db_status, db_status.upper())
            
            desc_mapping = {
                'berhasil': 'Pembayaran Berhasil',
                'pending': 'Menunggu Pembayaran',
                'belum': 'Menunggu Pembayaran',
                'menunggu': 'Menunggu Pembayaran',
                'gagal': 'Pembayaran Gagal',
                'dibatalkan': 'Pembayaran Dibatalkan'
            }
            status_desc = desc_mapping.get(db_status, 'Status Tidak Diketahui')

            formatted_data = {
                "responseCode": "2001200",
                "responseMessage": "Success (from local database)",
                "originalPartnerReferenceNo": transaction.get('partner_reference_no') or transaction.get('order_id'),
                "originalReferenceNo": transaction.get('dana_reference_no') or transaction.get('order_id'),
                "transDateTime": transaction.get('created_time').isoformat() if transaction.get('created_time') else None,
                "paidTime": transaction.get('paid_time').isoformat() if transaction.get('paid_time') else None,
                "amount": {
                    "value": str(transaction.get('amount', 0)),
                    "currency": transaction.get('currency', 'IDR')
                },
                "transactionStatus": api_status,
                "transactionStatusDesc": status_desc,
                "merchantId": transaction.get('merchant_id'),
                "paymentMethod": transaction.get('payment_method'),
                "campaignName": transaction.get('campaign_name'),
                "campaignKategori": transaction.get('campaign_kategori'),
                "institutionName": transaction.get('institution_name'),
                "additionalInfo": transaction.get('raw_payload'),
                "source": "local_database"
            }

            return Response.success(data=formatted_data, message="Detail retrieved from local database")

        except Exception as e:
            import traceback
            print(f"[DETAIL] EXCEPTION: {traceback.format_exc()}")
            return Response.error(f"Detail error: {str(e)}", 500)

            return Response.error(f"Detail error: {str(e)}", 500)

    def queryUserProfile(self, accessToken):
        """
        Query DANA User Profile (untuk ambil foto/avatar)
        API: /dana/member/query/queryUserProfile.htm
        Ref: Adapted from DanaAuthService._queryUserProfile
        """
        try:
            # Use Widget Base URL
            baseUrl = Config.DANA_WIDGET_BASE_URL
            endpoint = "/dana/member/query/queryUserProfile.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            reqMsgId = str(uuid.uuid4()).replace('-', '')

            # Request Body sesuai dokumentasi DANA Widget API (Envelope Format)
            requestPayload = {
                "request": {
                    "head": {
                        "version": "2.0",
                        "function": "dana.member.query.queryUserProfile",
                        "clientId": Config.DANA_CLIENT_ID,
                        "clientSecret": Config.DANA_CLIENT_SECRET,
                        "reqTime": timestamp,
                        "reqMsgId": reqMsgId,
                        "accessToken": accessToken,
                        "reserve": "{}"
                    },
                    "body": {
                        "userResources": [
                            "AVATAR_URL",      # Avatar URL
                            "NICKNAME",        # Nickname
                            "FULLNAME",        # Full name
                            "LOGIN_ID"         # Phone/Login ID
                        ]
                    }
                },
                "signature": "" 
            }

            # Generate Signature based on 'request' object
            # Per DanaAuthService, we sign the minified JSON of 'request'
            requestBodyStr = json.dumps(requestPayload['request'], separators=(',', ':'))
            
            # Use internal signature generation if possible, or reimplement custom logic
            # Check if we have _generateSignatureCustom in this class, if not, verify self.generateSignature behavior
            # self.generateSignature usually works for standard SNAP. This endpoint is Widget style.
            # Let's try to reuse the logic from DanaAuthService roughly:
            
            # FIXED: Use correct method name _generateSignature
            # But wait, _generateSignature in this class generates: HTTP_METHOD + ":" + ENDPOINT + ":" + LOWERCASE(HEX(SHA256(minify(REQUEST_BODY)))) + ":" + TIMESTAMP
            # The Widget API signature might be just the RSA signature of the request body json?
            # DanaAuthService._queryUserProfile uses:
            # signature = base64.b64encode(signer.sign(digest)).decode('utf-8') of the body string directly.
            # So _generateSignature is NOT suitable if it prepends method/url/etc.
            # Let's check _generateSignature implementation again.
            # It does: stringToSign = f"{httpMethod}:{endpointUrl}:{bodyHash}:{timestamp}"
            # This is SNAP signature. Widget API needs simple body signature.
            # So I should NOT use _generateSignature. I should keep the custom RSA implementation I added below it.
            # The error happened because I called self.generateSignature casually in the code block I added, 
            # while also having the custom RSA block below it? 
            # Looking at previous code (Step 604 diff), I had:
            # signature = self.generateSignature('POST', endpoint, requestPayload['request']) 
            # AND THEN:
            # if CRYPTO_AVAILABLE: ... requestPayload['signature'] = signature
            # I must REMOVE the call to self.generateSignature/self._generateSignature and rely solely on the explicit RSA signing block
            # because Widget API signature != SNAP signature.

            
            stringToSign = requestBodyStr
            
            # --- Quick RSA Sign Implementation (Copy from DanaAuthService) ---
            if CRYPTO_AVAILABLE:
                privateKey = Config.DANA_PRIVATE_KEY
                if '\\n' in privateKey: privateKey = privateKey.replace('\\n', '\n')
                if not privateKey.startswith('-----BEGIN'):
                    keyBody = privateKey.strip()
                    lines = [keyBody[i:i+64] for i in range(0, len(keyBody), 64)]
                    formattedKey = '\n'.join(lines)
                    privateKey = f"-----BEGIN RSA PRIVATE KEY-----\n{formattedKey}\n-----END RSA PRIVATE KEY-----"
                
                pkey = RSA.importKey(privateKey)
                signer = PKCS1_v1_5.new(pkey)
                digest = SHA256.new()
                digest.update(stringToSign.encode('utf-8'))
                signature = base64.b64encode(signer.sign(digest)).decode('utf-8')
                requestPayload['signature'] = signature
            # -----------------------------------------------------------------

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-CLIENT-KEY': Config.DANA_CLIENT_ID,
            }
            
            print(f"[DANA API] Query User Profile: {fullUrl}")
            
            # Serialize final payload
            finalPayloadStr = json.dumps(requestPayload, separators=(',', ':'))
            
            # Execute request
            response = requests.post(fullUrl, data=finalPayloadStr, headers=headers, timeout=10)
            data = response.json()
            
            # print(f"[DANA API] Response: {json.dumps(data)}")
            
            if 'response' in data and 'body' in data['response']:
                body = data['response']['body']
                resultInfo = body.get('resultInfo', {})
                
                if resultInfo.get('resultCode') == 'SUCCESS' or resultInfo.get('resultStatus') == 'S':
                    # Parse resources
                    userResourceInfos = body.get('userResourceInfos', [])
                    profileData = {}
                    for resource in userResourceInfos:
                        resType = resource.get('resourceType')
                        resValue = resource.get('value')
                        profileData[resType] = resValue
                    return profileData
                else:
                    print(f"[DANA API] Query User Profile Failed: {resultInfo.get('resultMsg')}")
                    return None
            return None
            
        except Exception as e:
            print(f"[DANA API] Query User Profile Exception: {str(e)}")
            return None

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
            print(f"WEBHOOK RECEIVED: {json.dumps(data)}")
            try:
                conn = self.db.getConnection()
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO log_dana_webhook
                        (webhook_type, order_id, dana_reference_no, payload, signature, created_date)
                        VALUES (%s, %s, %s, %s::jsonb, %s, %s)
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
                try:
                    conn.rollback()
                except:
                    pass


            # Cari donation
            donation = None
            if orderId:
                donation = self.donationModel.findByOrderId(orderId)
                print(f"[WEBHOOK] Searching donation by orderId: {orderId}, Found: {donation is not None}")
            if not donation and partnerRef:
                donation = self.donationModel.findByPartnerRefNo(partnerRef)
                print(f"[WEBHOOK] Searching donation by partnerRef: {partnerRef}, Found: {donation is not None}")

            if not donation:
                print(f"[WEBHOOK] Donation not found! orderId={orderId}, partnerRef={partnerRef}")
                # Return success anyway to acknowledge webhook
                # DANA expects 2xx response
                return {
                    "responseCode": "2005600",
                    "responseMessage": "Successful"
                }, 200

            print(f"[WEBHOOK] Donation found: {donation.get('order_id')}, Current status: {donation.get('status')}")

            # Update Database Status
            try:
                # Normalize status
                normalizedStatus = status.upper() if status else 'PENDING'

                # Map DANA status to readable format for logging
                status_display_map = {
                    'SUCCESS': 'SUCCESS (berhasil)',
                    '00': 'SUCCESS (berhasil)',
                    'PAID': 'PAID (berhasil)',
                    'FAILED': 'FAILED (gagal)',
                    'CANCELLED': 'CANCELLED (dibatalkan)',
                    'PENDING': 'PENDING (menunggu)'
                }
                display_status = status_display_map.get(normalizedStatus, normalizedStatus)
                print(f"[WEBHOOK] Updating donation status: {normalizedStatus} → {display_status}")

                # Update donation table (adm_campaign_donasi)
                # Fix: Pass raw API status to updateDanaStatusRef because it handles mapping internally
                # api_status can be 'SUCCESS', 'PENDING', etc.
                self.donationModel.updateDanaStatusRef(
                    donation.get('order_id'), 
                    donation.get('dana_reference_no'), 
                    normalizedStatus # Ensure uppercase for STATUS_MAP 
                )
                
                # Fetch fresh from DB to return latest status
                # Fix: Use the order_id from the EXISTING donation object, not the potentially-partner-ref 'orderId' variable
                # AND don't overwrite the main 'donation' variable if the fetch fails (safety)
                updated_donation = self.donationModel.findByOrderId(donation.get('order_id'))
                if updated_donation:
                    donation = updated_donation
                
                # Update log_dana_transaction table (so History page updates)
                logModel = LogDanaTransactionModel()
                # Use donation['order_id'] (DANA-...) not webhook orderId (which could be CINTA-...)
                correctOrderId = donation['order_id']
                
                logModel.updateStatus(
                    correctOrderId, 
                    normalizedStatus, 
                    data.get('transactionStatusDesc', 'Updated from webhook'),
                    datetime.now() if normalizedStatus in ['SUCCESS', '00', 'PAID'] else None,
                    datetime.now() if normalizedStatus in ['SUCCESS', '00', 'PAID'] else None
                )
                print(f"[WEBHOOK] Synced status to log_dana_transaction: {correctOrderId} -> {normalizedStatus}")

                # Sync to SIMBA if success
                is_success = normalizedStatus in ['SUCCESS', '00', 'PAID'] 
                if is_success:
                    print(f"[WEBHOOK] ✅ Triggering SIMBA sync for order: {donation['order_id']}")
                    self._syncToSimba(donation)
                else:
                     print(f"[WEBHOOK] Status {normalizedStatus} is not success, skipping SIMBA sync")      

            except Exception as dbErr:
                print(f"DB update failed: {str(dbErr)}")
                import traceback
                traceback.print_exc()

                # Log/Update transaction to log_dana_transaction table
                # We already tried to update status above. If it succeeded, we don't need to create a new record.
                # Only create if updateStatus failed (meaning record doesn't exist)
                
                # Check if updateStatus was already called successfully
                # We called logModel.updateStatus(correctOrderId...) earlier at line ~1489
                # Let's verify if we should create a new record or not.
                
                # To be safe, let's try to find if it exists first
                existing_log = logModel.findLatestByOrderId(donation.get('order_id'))
                
                if not existing_log:
                    # Create new log only if not exists
                    print(f"[LOG_DANA] No existing log found for {donation.get('order_id')}, creating new one.")
                    
                    # Extract payment info
                    additionalInfo = data.get('additionalInfo', {})
                    paymentInfo = additionalInfo.get('paymentInfo', {}) if isinstance(additionalInfo, dict) else {}
                    payOptionInfos = paymentInfo.get('payOptionInfos', []) if isinstance(paymentInfo, dict) else []
                    paymentMethod = payOptionInfos[0].get('payMethod', '') if payOptionInfos else ''
                    paidTime = paymentInfo.get('paidTime', '') if isinstance(paymentInfo, dict) else ''
                    
                    # Extract currency and statusDesc safely
                    currency = 'IDR'
                    if isinstance(data.get('amount'), dict):
                        currency = data.get('amount', {}).get('currency', 'IDR')
                    
                    statusDesc = data.get('transactionStatusDesc') or \
                                 data.get('statusMessage') or \
                                 data.get('responseMessage') or \
                                 'Webhook received'

                    logModel.create({
                        'order_id': donation.get('order_id'),
                        'partner_reference_no': partnerRef,
                        'dana_reference_no': danaRef,
                        'merchant_id': data.get('merchantId', ''),
                        'amount': amount,
                        'currency': currency,
                        'status': status,
                        'status_desc': statusDesc,
                        'created_time': data.get('createdTime'),
                        'finished_time': data.get('finishedTime'),
                        'paid_time': paidTime,
                        'payment_method': paymentMethod,
                        'user_id': donation.get('created_by', '').replace('user_', '') if donation.get('created_by', '').startswith('user_') else None,
                        'email': donation.get('email', ''),
                        'phone': donation.get('handphone', ''),
                        'raw_payload': data
                    })
                else:
                    print(f"[LOG_DANA] Log already exists/updated for {donation.get('order_id')}, skipping creation.")

            except Exception as logErr:
                print(f"[LOG_DANA] Failed to log webhook transaction: {logErr}")
                import traceback
                traceback.print_exc()

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

    def getHistory(self, userId=None, month=None, year=None, status=None, limit=20, offset=0):
        """
        Get transaction history for Mini App
        Strategy:
        1. Try to get from DANA API if user has access token (filtered by date)
        2. Fallback to local database
        """
        try:
            # Check user access token
            accessToken = None
            if userId:
                user = self.userModel.findById(userId)
                if user:
                    accessToken = user.get('dana_access_token')

            # 1. Try DANA API
            if accessToken:
                try:
                    # Calculate dates
                    now = datetime.now()
                    target_year = int(year) if year else now.year
                    target_month = int(month) if month else now.month
                    
                    import calendar
                    _, last_day = calendar.monthrange(target_year, target_month)
                    
                    # Create aware datetime objects (UTC)
                    # Note: DANA expects UTC for fromDateTime/toDateTime
                    start_date = datetime(target_year, target_month, 1, 0, 0, 0)
                    end_date = datetime(target_year, target_month, last_day, 23, 59, 59)
                    
                    # Convert to format: YYYY-MM-DDTHH:mm:ssZ
                    fromInit = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    toInit = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    
                    print(f"[HISTORY] Fetching from DANA API: {fromInit} to {toInit}")
                    
                    api_result = self._callDanaTransactionHistoryApi(
                        accessToken, 
                        page=(int(offset) // int(limit)) + 1, 
                        pageSize=limit, 
                        fromDate=fromInit,
                        toDate=toInit
                    )
                    
                    if api_result['success'] and api_result.get('data', {}).get('detailData'):
                        print("[HISTORY] Got data from DANA API")
                        # Map DANA data
                        dana_txs = api_result['data']['detailData']
                        mapped_results = []
                        
                        for tx in dana_txs:
                            mapped_results.append({
                                "referenceNo": tx.get('referenceNo'),
                                "originalReferenceNo": tx.get('partnerReferenceNo'),
                                "merchantId": self.merchantId,
                                "transactionStatus": tx.get('status'),
                                "status": tx.get('status'),
                                "transDateTime": tx.get('dateTime'), # Already formatted from DANA
                                "dateTime": tx.get('dateTime'),
                                "amount": tx.get('amount'),
                                "campaignName": tx.get('remark') or "Donasi DANA",
                                "institutionName": "BAZNAS",
                                "source": "dana_api"
                            })
                            
                        # Filter by status if needed (client side filter since API returns list)
                        if status and status.lower() != 'all':
                             # map frontend status 'success' -> 'SUCCESS'
                             target_status = 'SUCCESS' if status.lower() == 'berhasil' else \
                                             'PENDING' if status.lower() == 'pending' else \
                                             status.upper()
                             
                             mapped_results = [r for r in mapped_results if r['status'] == target_status]

                        return Response.success(
                            data={"detailData": mapped_results}, 
                            message="History retrieved from DANA API"
                        )
                except Exception as apiErr:
                    print(f"[HISTORY] DANA API Attempt Failed: {str(apiErr)}")
                    # Continue to fallback
            
            # 2. Fallback to Local DB
            conn = self.db.getConnection()
            results = []
            
            # Build query
            sql = """
                SELECT 
                    d.order_id, d.partner_reference_no, d.status, d.tgl_donasi, d.nominal,
                    c.name as campaign_name, c.kategori
                FROM adm_campaign_donasi d
                LEFT JOIN adm_campaign c ON d.campaign_id = c.id
                WHERE 1=1
            """
            params = []
            
            # Filter by User (either user_id or created_by logic)
            # Prioritize userId if provided (from token)
            if userId:
                # Check based on created_by user_{id} or email/phone match if needed
                # Simplest is created_by = 'user_{userId}'
                sql += " AND d.created_by = %s"
                params.append(f"user_{userId}")
            
            # Filter by Month/Year
            if month:
                sql += " AND EXTRACT(MONTH FROM d.tgl_donasi) = %s"
                params.append(month)
            if year:
                sql += " AND EXTRACT(YEAR FROM d.tgl_donasi) = %s"
                params.append(year)
                
            # Filter by Status
            if status:
                if status.lower() == 'berhasil':
                    sql += " AND d.status = 'berhasil'"
                elif status.lower() == 'pending':
                    sql += " AND d.status IN ('belum', 'menunggu', 'pending')"
                elif status.lower() != 'all':
                    sql += " AND d.status = %s"
                    params.append(status.lower())
            
            # Order and Pagination
            sql += " ORDER BY d.tgl_donasi DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()
                
                for row in rows:
                    # Map params
                    orderId = row.get('order_id')
                    partnerRef = row.get('partner_reference_no')
                    trxStatus = row.get('status')
                    tglDonasi = row.get('tgl_donasi')
                    nominal = row.get('nominal')
                    campaignName = row.get('campaign_name')
                    kategori = row.get('kategori')
                    
                    # Format Status for Frontend
                    statusMap = {
                        'berhasil': 'SUCCESS',
                        'pending': 'PENDING',
                        'belum': 'PENDING',
                        'menunggu': 'PENDING',
                        'gagal': 'FAILED',
                        'dibatalkan': 'FAILED',
                        'expired': 'EXPIRED'
                    }
                    displayStatus = statusMap.get(trxStatus, trxStatus.upper())
                    
                    results.append({
                        "referenceNo": orderId,
                        "originalReferenceNo": partnerRef,
                        "merchantId": self.merchantId,
                        "transactionStatus": displayStatus,
                        "status": displayStatus,
                        "transDateTime": tglDonasi.strftime('%Y-%m-%dT%H:%M:%S+07:00') if tglDonasi else '',
                        "dateTime": tglDonasi.strftime('%Y-%m-%dT%H:%M:%S+07:00') if tglDonasi else '',
                        "amount": {
                            "value": str(int(nominal)) if nominal else "0",
                            "currency": "IDR"
                        },
                        "campaignName": campaignName or "Donasi",
                        "institutionName": "BAZNAS RI (Pusat)",
                        "source": "local_database"
                    })
            
            return Response.success(data={"detailData": results}, message="History retrieved form local DB")

        except Exception as e:
            print(f"[History] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "responseCode": "500",
                "responseMessage": f"Internal Error: {str(e)}",
                "detailData": []
            }

    def _mapDanaStatus(self, danaStatus):
        """Map DANA status ke internal status"""
        if not danaStatus:
            return 'pending'

        statusMap = {
            'SUCCESS': 'berhasil',
            '00': 'berhasil',
            'PAID': 'berhasil',
            'COMPLETED': 'berhasil',
            '00': 'berhasil',  # Finish Notify Success Code
            'FAILED': 'gagal',
            'CANCELLED': 'dibatalkan',
            '05': 'dibatalkan', # Finish Notify Cancelled Code
            'EXPIRED': 'expired',
            'PENDING': 'pending',
            'INIT': 'pending'
        }
        return statusMap.get(danaStatus.upper(), 'pending')

    def _syncToSimba(self, donation):
        """
        Sync transaksi ke SIMBA setelah sukses
        Flow:
        1. Cek apakah donation punya muzaki_id
        2. Jika tidak, create muzaki record
        3. Register muzaki ke SIMBA → dapat NPWZ
        4. Update NPWZ di database (muzaki & donation)
        5. Save transaction ke SIMBA
        """
        try:
            from src.services.simba_integration import SimbaIntegration
            from src.models.muzaki_model import MuzakiModel

            print(f"[SIMBA] === Starting SIMBA sync for order {donation.get('order_id')} ===")

            # Initialize SIMBA integration
            simba = SimbaIntegration()
            muzakiModel = MuzakiModel()

            # Get fresh donation data
            donation = self.donationModel.findByOrderId(donation['order_id'])
            if not donation:
                print(f"[SIMBA] Donation not found")
                return

            # Step 1: Get or create muzaki
            muzaki_id = donation.get('muzaki_id')
            muzaki = None

            if muzaki_id:
                # Try to find existing muzaki
                muzaki = muzakiModel.findById(muzaki_id)
                if muzaki:
                    print(f"[SIMBA] Existing muzaki found: {muzaki_id}")
                    
                    # Backfill donation name if it was empty/default
                    # Also try to resolve Name from User if we haven't already
                    current_donation_name = donation.get('nama_lengkap')
                    donation_hamba_allah = donation.get('hamba_allah')
                    
                    if not current_donation_name or current_donation_name == 'Hamba Allah' or current_donation_name == '':
                        # Need to find the REAL name to backfill
                        real_name = muzaki.get('nama')
                        
                        # If muzaki name is also generic, try to find from User Profile
                        if not real_name or real_name == 'Hamba Allah' or real_name.replace('0','').replace('8','').isdigit():
                             created_by = donation.get('created_by', '')
                             if created_by and created_by.startswith('user_'):
                                 try:
                                     user_id = created_by.split('_')[1]
                                     localUserModel = UserModel()
                                     user = localUserModel.findById(user_id)
                                     if user:
                                         user_name = user.get('nama') or user.get('name') or user.get('full_name')
                                         if user_name:
                                             real_name = user_name
                                             print(f"[SIMBA] Resolved real name from User profile: {real_name}")
                                     localUserModel.conn.close()
                                 except Exception as e:
                                     print(f"[SIMBA] Failed to lookup user for backfill: {e}")

                        if real_name and real_name != 'Hamba Allah' and real_name != 'Tidak Diketahui':
                             print(f"[SIMBA] Backfilling donation name from '{current_donation_name}' to '{real_name}'")
                             try:
                                 # Use existing connection from donationModel safely
                                 with self.donationModel.conn.cursor() as cursor:
                                    # Update name AND set hamba_allah = 'N' so it shows up
                                    # Also update updated_date
                                    sql = f"UPDATE {self.donationModel.table_name} SET nama_lengkap = %s, hamba_allah = 'N', updated_date = %s WHERE order_id = %s"
                                    cursor.execute(sql, (real_name, datetime.now(), donation['order_id']))
                                    self.donationModel.conn.commit()
                                    print(f"[SIMBA] Name backfilled and hamba_allah set to 'N' for order {donation['order_id']}")
                             except Exception as e:
                                 print(f"[SIMBA] Failed to backfill name: {e}")
                                 self.donationModel.conn.rollback()
                else:
                    print(f"[SIMBA] ⚠️ Muzaki ID {muzaki_id} not found in database! Will try to find/create.")
                    muzaki_id = None  # Reset to trigger search/create flow

            if not muzaki_id:
                # Try to find existing muzaki by email or phone
                email = donation.get('email', '')
                
                # Get user data - try multiple methods
                user_name = None
                user_phone = ''
                user = None
                
                # Method 1: Try to get user by created_by (might be user_id)
                created_by = donation.get('created_by', '')
                if created_by and created_by.startswith('user_'):
                    try:
                        user_id = int(created_by.replace('user_', ''))
                        user = self.userModel.findById(user_id)
                        if user:
                            print(f"[SIMBA] Found user by created_by: {user_id}")
                    except Exception as e:
                        print(f"[SIMBA] Error parsing created_by: {e}")
                
                # Method 2: Try to get user by email
                if not user and email:
                    try:
                        user = self.userModel.findByEmail(email)
                        if user:
                            print(f"[SIMBA] Found user by email: {email}")
                    except Exception as userErr:
                        print(f"[SIMBA] Error fetching user by email: {userErr}")
                
                # Extract user data
                if user:
                    # Map database fields correctly: full_name (not name), handphone (not phone)
                    user_name = user.get('full_name') or user.get('username')
                    user_phone = user.get('handphone', '')
                    # Remove country code prefix if exists (62- → empty)
                    if user_phone and user_phone.startswith('62-'):
                        user_phone = user_phone.replace('62-', '')
                    print(f"[SIMBA] User data: name={user_name}, phone={user_phone}")
                else:
                    print(f"[SIMBA] No user found for email={email}, created_by={created_by}")
                
                # Determine final name - use whatever is available, just skip "Hamba Allah"
                final_name = user_name
                
                # If name is "Hamba Allah" or empty, use phone number instead
                if not final_name or final_name.lower() == 'hamba allah':
                    final_name = user_phone if user_phone else 'Tidak Diketahui'
                    print(f"[SIMBA] Name is 'Hamba Allah' or empty, using: {final_name}")
                else:
                    print(f"[SIMBA] Using name from user: {final_name}")
                
                muzaki = muzakiModel.findByEmailOrPhone(email, user_phone)
                
                if muzaki:
                    print(f"[SIMBA] Found existing muzaki by email/phone: {muzaki.get('id')}")
                    # Link donation to muzaki
                    self.donationModel.updateMuzakiId(donation['order_id'], muzaki['id'])
                    muzaki_id = muzaki['id']
                    
                    # Backfill donation name if it was empty/default and we found a better name
                    current_donation_name = donation.get('nama_lengkap')
                    
                    # Robust check for hamba_allah flag
                    hamba_val = donation.get('hamba_allah')
                    is_hamba_allah = str(hamba_val).upper() in ['Y', 'TRUE', '1', 'T'] if hamba_val is not None else False

                    print(f"[SIMBA] Donation {donation['order_id']} - Name: {current_donation_name}, Hamba Allah: {is_hamba_allah} (Val: {hamba_val})")

                    if not current_donation_name or current_donation_name == 'Hamba Allah' or current_donation_name == '':
                         # ONLY backfill if user is NOT hamba_allah
                         if not is_hamba_allah:
                             if final_name and final_name != 'Hamba Allah' and final_name != 'Tidak Diketahui':
                                 print(f"[SIMBA] Backfilling donation name from '{current_donation_name}' to '{final_name}'")
                                 try:
                                     with self.donationModel.conn.cursor() as cursor:
                                        # Also update updated_date
                                        sql = f"UPDATE {self.donationModel.table_name} SET nama_lengkap = %s, hamba_allah = 'N', updated_date = %s WHERE order_id = %s"
                                        cursor.execute(sql, (final_name, datetime.now(), donation['order_id']))
                                        self.donationModel.conn.commit()
                                        print(f"[SIMBA] Name backfilled and hamba_allah set to 'N' for order {donation['order_id']}")
                                 except Exception as e:
                                     print(f"[SIMBA] Failed to backfill name: {e}")
                                     self.donationModel.conn.rollback()
                         else:
                             print(f"[SIMBA] User requested 'Hamba Allah', skipping name backfill.")
                             # Optional: Ensure it IS 'Hamba Allah' in DB if it was empty
                             if current_donation_name != 'Hamba Allah':
                                 try:
                                     with self.donationModel.conn.cursor() as cursor:
                                        sql = f"UPDATE {self.donationModel.table_name} SET nama_lengkap = 'Hamba Allah', updated_date = %s WHERE order_id = %s"
                                        cursor.execute(sql, (datetime.now(), donation['order_id']))
                                        self.donationModel.conn.commit()
                                        print(f"[SIMBA] Enforced 'Hamba Allah' name for order {donation['order_id']}")
                                 except:
                                     pass
                else:
                    # Create new muzaki
                    print(f"[SIMBA] Creating new muzaki")
                    try:
                        muzaki_data = {
                            'tipe': donation.get('tipe', 'perorangan'),
                            'nama': final_name,  # Use final_name (phone number for DANA seamless login)
                            'email': email,
                            'handphone': user_phone,
                            'npwz': '',
                            'npwz_bg': '',
                            'tgl_daftar': datetime.now().strftime('%Y-%m-%d'),
                            'created_by': 'system_webhook'
                        }
                        print(f"[SIMBA] Muzaki data: {muzaki_data}")
                        muzaki_id = muzakiModel.create(muzaki_data)
                        
                        if muzaki_id:
                            print(f"[SIMBA] New muzaki created: {muzaki_id}")
                            # Link donation to muzaki
                            self.donationModel.updateMuzakiId(donation['order_id'], muzaki_id)
                            muzaki = muzakiModel.findById(muzaki_id)
                        else:
                            print(f"[SIMBA] Failed to create muzaki - create() returned None/False")
                            return
                        return
                    except Exception as createErr:
                        print(f"[SIMBA] Error creating muzaki: {createErr}")
                        import traceback
                        traceback.print_exc()
                        return

            # --- NEW: Update Foto from DANA Profile if available ---
            if muzaki_id and user:
                try:
                    # Check if user has DANA access token
                    accessToken = self.userModel.getDanaAccessToken(user['id'])
                    if accessToken:
                        print(f"[SIMBA] Fetching DANA User Profile for photo update...")
                        danaProfile = self.queryUserProfile(accessToken)
                        if danaProfile:
                            avatarUrl = danaProfile.get('AVATAR_URL')
                            if avatarUrl:
                                print(f"[SIMBA] Updating Muzaki {muzaki_id} photo from DANA: {avatarUrl}")
                                muzakiModel.updateFoto(muzaki_id, avatarUrl)
                            else:
                                print(f"[SIMBA] No AVATAR_URL in DANA profile")
                        else:
                            print(f"[SIMBA] Failed to get DANA profile")
                    else:
                        print(f"[SIMBA] User {user['id']} has no valid DANA access token. Skipping photo update.")
                except Exception as photoErr:
                    print(f"[SIMBA] Error updating photo from DANA: {photoErr}")
            # -------------------------------------------------------

            # Step 2: Register muzaki to SIMBA if no NPWZ
            if not muzaki:
                print(f"[SIMBA] ❌ ERROR: No muzaki found/created. Cannot proceed with SIMBA sync.")
                return

            npwz = muzaki.get('npwz') if muzaki else None

            if not npwz or npwz == '' or npwz == '0':
                print(f"[SIMBA] Registering muzaki to SIMBA")
                print(f"[SIMBA] Muzaki info - Nama: {muzaki.get('nama')}, Email: {muzaki.get('email')}, Phone: {muzaki.get('handphone')}")
                
                register_result = simba.registerMuzaki(
                    nama=muzaki.get('nama', 'Tidak Diketahui'),
                    email=muzaki.get('email', ''),
                    handphone=muzaki.get('handphone', ''),
                    tipe=muzaki.get('tipe', 'perorangan')
                )
                
                print(f"[SIMBA] Register result: {register_result}")
                
                if register_result.get('success'):
                    npwz = register_result.get('npwz', '0')
                    print(f"[SIMBA] Muzaki registered. NPWZ: {npwz}")
                    
                    # Update NPWZ in database
                    if muzaki_id:
                        muzakiModel.updateNpwz(muzaki_id, npwz, npwz)
                    self.donationModel.updateNpwz(donation['order_id'], npwz)
                else:
                    error = register_result.get('error', 'Unknown error')
                    response = register_result.get('response', {})
                    print(f"[SIMBA] Muzaki registration failed: {error}")
                    print(f"[SIMBA] Full response: {response}")
                    # Continue with npwz = '0'
                    npwz = '0'
                    # Continue with npwz = '0'
                    npwz = '0'
            else:
                print(f"[SIMBA] Using existing NPWZ: {npwz}")
                # Backfill NPWZ to donation if missing
                if not donation.get('npwz') and npwz:
                     print(f"[SIMBA] Backfilling NPWZ {npwz} to donation {donation['order_id']}")
                     self.donationModel.updateNpwz(donation['order_id'], npwz)

            # Step 3: Save transaction to SIMBA
            print(f"[SIMBA] Saving transaction to SIMBA")

            # Re-enforce status 'berhasil' just in case
            if donation.get('status') != 'berhasil':
                 print(f"[SIMBA] Re-enforcing status 'berhasil' for order {donation['order_id']}")
                 # We use 'SUCCESS' which maps to 'berhasil'
                 self.donationModel.updateDanaStatusRef(donation['order_id'], donation.get('dana_reference_no'), 'SUCCESS')

            # Format tanggal untuk SIMBA (dd/mm/yyyy)
            tgl_donasi = donation.get('tgl_donasi')
            if isinstance(tgl_donasi, str):
                try:
                    tgl_donasi = datetime.strptime(tgl_donasi, '%Y-%m-%d')
                except:
                    tgl_donasi = datetime.now()
            elif not tgl_donasi:
                tgl_donasi = datetime.now()

            tanggal_simba = tgl_donasi.strftime('%d/%m/%Y')

            # Get tipe zakat (legacy support)
            tipe_zakat = donation.get('tipe_zakat', 'infak')

            # Map tipe_zakat to readable format for SIMBA (legacy)
            tipe_zakat_map = {
                'zakat': 'zakat penghasilan',  # Default zakat
                'infak': 'infak',
                'fidyah': 'fidyah'
            }
            tipe_zakat_simba = tipe_zakat_map.get(tipe_zakat.lower(), 'infak')

            # NEW: Get campaign data for proper kode program and kode akun mapping
            campaign_kategori = None
            campaign_tipe = None
            campaign_coa = None
            campaign_name = None

            campaign_id = donation.get('campaign_id')
            if campaign_id:
                try:
                    from src.models.campaign_model import CampaignModel
                    campaignModel = CampaignModel()
                    campaign = campaignModel.findById(campaign_id)

                    if campaign:
                        campaign_kategori = campaign.get('kategori')
                        campaign_tipe = campaign.get('tipe')
                        campaign_name = campaign.get('name')  # NEW: Get campaign name
                        program_id = campaign.get('program_id')  # Get program_id

                        # Get appropriate COA based on tipe
                        if campaign_tipe == 'zakat':
                            campaign_coa = campaign.get('coa_zakat')
                        else:
                            campaign_coa = campaign.get('coa_infak')

                        # Get program code from ref_dana_sosial if program_id exists
                        campaign_program_code = None
                        if program_id:
                            try:
                                conn = self.db.getConnection()
                                with conn.cursor() as cursor:
                                    cursor.execute(
                                        "SELECT code FROM ref_dana_sosial WHERE id = %s AND is_delete = 'N'",
                                        (program_id,)
                                    )
                                    program_row = cursor.fetchone()
                                    if program_row:
                                        campaign_program_code = program_row.get('code')
                                        print(f"[SIMBA] Found program code from ref_dana_sosial: {campaign_program_code}")
                            except Exception as progErr:
                                print(f"[SIMBA] Error fetching program code: {progErr}")

                        print(f"[SIMBA] Campaign data found - Name: {campaign_name}, Kategori: {campaign_kategori}, Tipe: {campaign_tipe}, COA: {campaign_coa}, Program Code: {campaign_program_code}")
                    else:
                        print(f"[SIMBA] Campaign {campaign_id} not found, using legacy mapping")

                    # Close campaign model connection
                    campaignModel.conn.close()
                except Exception as campaignErr:
                    print(f"[SIMBA] Error fetching campaign data: {campaignErr}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[SIMBA] No campaign_id in donation, using legacy mapping")

            save_result = simba.saveTransaction(
                npwz=npwz,
                amount=int(donation.get('nominal', 0)),
                tanggal=tanggal_simba,
                tipe_zakat=tipe_zakat_simba,  # Legacy support
                order_id=donation.get('order_id', ''),
                campaign_kategori=campaign_kategori,  # NEW
                campaign_tipe=campaign_tipe,  # NEW
                campaign_coa=campaign_coa,  # NEW
                campaign_name=campaign_name,  # NEW: Pass campaign name
                campaign_program_code=campaign_program_code  # NEW: Pass program code from ref_dana_sosial
            )
            
            if save_result.get('success'):
                no_transaksi = save_result.get('no_transaksi', '')
                print(f"[SIMBA] ✅ Transaction synced to SIMBA. Transaksi No: {no_transaksi}")

                # Update donation dengan no_transaksi SIMBA
                # Update donation dengan no_transaksi SIMBA dan info waktu
                try:
                    conn = self.db.getConnection()
                    with conn.cursor() as cursor:
                        # Fix: Populate tanggal, waktu, and transaksi_id as requested
                        current_dt = datetime.now()
                        tanggal_str = current_dt.strftime('%Y-%m-%d')
                        waktu_str = current_dt.strftime('%H:%M:%S')
                        
                        sql = """
                            UPDATE adm_campaign_donasi 
                            SET no_transaksi = %s, 
                                transaksi_id = %s,
                                tanggal = %s,
                                waktu = %s,
                                updated_date = %s
                            WHERE order_id = %s
                        """
                        cursor.execute(sql, (
                            no_transaksi, 
                            no_transaksi, # Use SIMBA Id as transaksi_id per request context
                            tanggal_str, 
                            waktu_str, 
                            current_dt,
                            donation['order_id']
                        ))
                        conn.commit()
                        print(f"[SIMBA] Updated transaction info: No={no_transaksi}, Date={tanggal_str}, Time={waktu_str}")
                except Exception as updateErr:
                    print(f"[SIMBA] Failed to update no_transaksi: {updateErr}")
            else:
                error = save_result.get('error', 'Unknown error')
                print(f"[SIMBA] Transaction save failed: {error}")

            print(f"[SIMBA] === SIMBA sync completed ===")

        except Exception as e:
            print(f"[SIMBA] SIMBA sync failed: {str(e)}")
            import traceback
            traceback.print_exc()

    def finishPayment(self, data):
        """
        Handle finish payment callback dari DANA atau mini app

        Endpoint ini dipanggil setelah user selesai pembayaran:
        - Dari DANA redirect callback
        - Dari mini app setelah my.tradePay success
        - Dari dev_mode simulation
        """
            # Fallback for NOTIFICATION type urlParams logic if validUpTo or notificationUrl points here
        # Check if this is a DANA Webhook payload
        if 'latestTransactionStatus' in data or 'originalPartnerReferenceNo' in data:
            print("Redirecting finishPayment to webhook handler...")
            # Headers might be needed for signature, but likely missing if internal call
            # We pass empty headers/signature if not available in current scope (or grab from request if flask context allowed, but this is service layer)
            # Since finishPayment doesn't receive signature/headers args in service, we might miss signature verification here.
            # However, logic-wise it handles the DB update.
            return self.webhook(data)

        orderId = data.get('orderId') or data.get('merchantTransId')
        resultCode = data.get('resultCode')
        resultStatus = data.get('resultStatus')
        devMode = data.get('dev_mode', False)

        if not orderId:
            return Response.success(data={
                "message": "Callback received (Ignored - No Order ID)",
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
