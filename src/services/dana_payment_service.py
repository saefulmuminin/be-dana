"""
DANA Payment Integration Service
Menggunakan library resmi dana-python untuk integrasi Payment Widget Binding

Dokumentasi: https://dashboard.dana.id/api-docs
Library: pip install dana-python
"""

from src.models.donation_model import DonationModel
from src.models.master_models import RefPaymentModel, RefCampaignModel
from src.services.simba_service import SimbaService
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime
import uuid
import json

# Import DANA official library
try:
    from dana.payment_gateway import v1 as dana_payment
    from dana.ipg import v1 as dana_ipg  # Integrated Payment Gateway (Widget)
    DANA_SDK_AVAILABLE = True
except ImportError:
    DANA_SDK_AVAILABLE = False
    print("WARNING: dana-python library not installed. Run: pip install dana-python")


class DanaPaymentService:
    """
    DANA Payment Integration Service menggunakan DANA Widget Binding
    (Integrated Payment Widget untuk seamless login & payment)
    """

    def __init__(self):
        self.donationModel = DonationModel()
        self.paymentModel = RefPaymentModel()
        self.campaignModel = RefCampaignModel()
        self.simbaService = SimbaService()
        self.db = Database()

        # DANA Credentials dari config
        self.merchantId = Config.DANA_MERCHANT_ID
        self.partnerId = Config.DANA_CLIENT_ID  # X_PARTNER_ID
        self.channelId = getattr(Config, 'DANA_CHANNEL_ID', 'channel_id')
        self.privateKey = getattr(Config, 'DANA_PRIVATE_KEY', None)
        self.privateKeyPath = getattr(Config, 'DANA_PRIVATE_KEY_PATH', None)
        self.origin = getattr(Config, 'DANA_ORIGIN', 'https://cintazakat.id')
        self.env = getattr(Config, 'DANA_ENV', 'sandbox')  # 'sandbox' atau 'production'

        # Fallback untuk implementasi tanpa SDK
        self.clientSecret = Config.DANA_CLIENT_SECRET
        self.baseUrl = Config.DANA_BASE_URL

    def _initDanaClient(self):
        """
        Initialize DANA SDK client
        """
        if not DANA_SDK_AVAILABLE:
            return None

        import os
        # Set environment variables untuk DANA SDK
        os.environ['X_PARTNER_ID'] = self.partnerId
        os.environ['MERCHANT_ID'] = self.merchantId
        os.environ['CHANNEL_ID'] = self.channelId
        os.environ['ORIGIN'] = self.origin
        os.environ['ENV'] = self.env

        if self.privateKey:
            os.environ['PRIVATE_KEY'] = self.privateKey
        elif self.privateKeyPath:
            os.environ['PRIVATE_KEY_PATH'] = self.privateKeyPath

        return True

    def logApiCall(self, endpoint, method, requestBody, responseStatus, responseBody,
                   orderId=None, duration=None, error=None):
        """
        Log API call ke database untuk debugging dan audit
        """
        try:
            conn = self.db.getConnection()
            with conn.cursor() as cursor:
                # Mask sensitive data
                safeRequest = self._maskSensitiveData(requestBody) if requestBody else None

                sql = """
                    INSERT INTO log_api
                    (name, aplikasi, url_api, parameter, response, created_date, created_by, is_active, is_delete)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y', 'N')
                """
                cursor.execute(sql, (
                    f"DANA_{method}_{orderId or 'unknown'}",
                    'DANA_WIDGET',
                    endpoint,
                    json.dumps(safeRequest) if safeRequest else None,
                    json.dumps(responseBody) if responseBody else str(error),
                    datetime.now(),
                    'system'
                ))
                conn.commit()
        except Exception as e:
            print(f"Failed to log API call: {str(e)}")

    def _maskSensitiveData(self, data):
        """
        Mask sensitive data untuk logging
        """
        if not data or not isinstance(data, dict):
            return data

        masked = data.copy()
        sensitiveKeys = ['accessToken', 'access_token', 'refreshToken',
                         'refresh_token', 'signature', 'privateKey', 'ottToken']

        for key in sensitiveKeys:
            if key in masked and masked[key]:
                value = str(masked[key])
                masked[key] = value[:8] + '***MASKED***' if len(value) > 8 else '***'

        return masked

    def createOrder(self, data):
        """
        Create payment order menggunakan DANA Widget Binding

        Flow:
        1. User sudah login via seamless (punya access_token)
        2. Buat order di backend
        3. Call DANA API untuk create payment request
        4. Return webRedirectUrl untuk user melanjutkan pembayaran

        Args:
            data: {
                access_token: DANA access token dari seamless login
                nominal: Jumlah donasi
                email: Email donatur
                campaign_id: ID campaign
                nama_lengkap, doa_muzaki, tipe_zakat, hamba_allah, muzaki_id (optional)
            }
        """
        try:
            # Validate input
            validation = self._validateCreateOrderInput(data)
            if not validation['valid']:
                return Response.error(validation['message'], 400)

            # Prepare donation data
            donationData = self._prepareDonationData(data)

            # Save to database first
            donationId = self.donationModel.create(donationData)
            if not donationId:
                return Response.error("Gagal menyimpan data donasi", 500)

            # Call DANA API
            if DANA_SDK_AVAILABLE:
                result = self._createOrderWithSDK(donationData, data.get('access_token'))
            else:
                result = self._createOrderFallback(donationData, data.get('access_token'))

            return result

        except Exception as e:
            self.logApiCall('create-order', 'POST', data, 500, None,
                           data.get('order_id'), error=str(e))
            return Response.error(f"Create order gagal: {str(e)}", 500)

    def _createOrderWithSDK(self, donation, accessToken):
        """
        Create order menggunakan DANA official SDK
        """
        try:
            self._initDanaClient()

            # Menggunakan DANA IPG (Integrated Payment Gateway) untuk Widget
            totalAmount = int(donation['nominal'] + donation['biaya_admin'])

            # Request body sesuai dokumentasi DANA Widget
            request_data = {
                "partnerReferenceNo": donation['partner_reference_no'],
                "merchantId": self.merchantId,
                "amount": {
                    "value": str(totalAmount) + ".00",
                    "currency": "IDR"
                },
                "urlParam": {
                    "url": f"{self.origin}/api/v1/dana/finish-payment",
                    "type": "PAY_RETURN",
                    "isDeeplink": "N"
                },
                "additionalInfo": {
                    "order": {
                        "orderTitle": f"Donasi {donation.get('tipe_zakat', 'Infak').upper()}",
                        "merchantTransId": donation['order_id']
                    }
                }
            }

            # Call DANA SDK
            response = dana_ipg.create_order(
                request_data,
                access_token=accessToken
            )

            self.logApiCall('dana_ipg.create_order', 'POST', request_data,
                           200, response, donation['order_id'])

            # Handle response
            if response.get('responseCode') in ['2005400', '2005401', '00']:
                referenceNo = response.get('referenceNo')
                webRedirectUrl = response.get('webRedirectUrl')

                self.donationModel.updateDanaRefs(
                    donation['order_id'], referenceNo, webRedirectUrl
                )

                return Response.success(data={
                    "orderId": donation['order_id'],
                    "partnerReferenceNo": donation['partner_reference_no'],
                    "referenceNo": referenceNo,
                    "webRedirectUrl": webRedirectUrl,
                    "amount": totalAmount
                }, message="Order berhasil dibuat")
            else:
                self.donationModel.updateStatus(donation['order_id'], 'failed')
                return Response.error(
                    f"DANA Error: {response.get('responseMessage', 'Unknown error')}",
                    400
                )

        except Exception as e:
            self.donationModel.updateStatus(donation['order_id'], 'failed')
            self.logApiCall('dana_ipg.create_order', 'POST', None, 500, None,
                           donation['order_id'], error=str(e))
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _createOrderFallback(self, donation, accessToken):
        """
        Fallback: Create order tanpa SDK (raw HTTP request)
        Gunakan ini jika dana-python tidak terinstall
        """
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        totalAmount = int(donation['nominal'] + donation['biaya_admin'])

        requestBody = {
            "partnerReferenceNo": donation['partner_reference_no'],
            "merchantId": self.merchantId,
            "amount": {
                "value": str(totalAmount) + ".00",
                "currency": "IDR"
            },
            "urlParam": {
                "url": f"{self.origin}/api/v1/dana/finish-payment",
                "type": "PAY_RETURN",
                "isDeeplink": "N"
            },
            "additionalInfo": {
                "order": {
                    "orderTitle": f"Donasi {donation.get('tipe_zakat', 'Infak').upper()}",
                    "merchantTransId": donation['order_id']
                }
            }
        }

        # Generate signature
        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/debit/payment-host-to-host"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "Authorization": f"Bearer {accessToken}",
            "CHANNEL-ID": self.channelId,
            "X-EXTERNAL-ID": donation['order_id']
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            self.logApiCall(url, 'POST', requestBody, response.status_code,
                           result, donation['order_id'])

            if response.status_code == 200 and result.get('responseCode') in ['2005400', '2005401', '00']:
                referenceNo = result.get('referenceNo')
                webRedirectUrl = result.get('webRedirectUrl')

                self.donationModel.updateDanaRefs(
                    donation['order_id'], referenceNo, webRedirectUrl
                )

                return Response.success(data={
                    "orderId": donation['order_id'],
                    "partnerReferenceNo": donation['partner_reference_no'],
                    "referenceNo": referenceNo,
                    "webRedirectUrl": webRedirectUrl,
                    "amount": totalAmount
                }, message="Order berhasil dibuat")
            else:
                self.donationModel.updateStatus(donation['order_id'], 'failed')
                return Response.error(
                    f"DANA Error: {result.get('responseMessage', response.text)}",
                    response.status_code
                )

        except requests.exceptions.Timeout:
            self.donationModel.updateStatus(donation['order_id'], 'failed')
            return Response.error("DANA API timeout", 504)
        except Exception as e:
            self.donationModel.updateStatus(donation['order_id'], 'failed')
            return Response.error(f"Request failed: {str(e)}", 500)

    def _validateCreateOrderInput(self, data):
        """Validasi input untuk create order"""
        if not data.get('access_token'):
            return {'valid': False, 'message': 'Access token wajib diisi'}

        nominal = data.get('nominal')
        if not nominal:
            return {'valid': False, 'message': 'Nominal donasi wajib diisi'}

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

        if not data.get('campaign_id'):
            return {'valid': False, 'message': 'Campaign ID wajib diisi'}

        return {'valid': True, 'message': 'OK'}

    def _prepareDonationData(self, data):
        """Siapkan data donasi untuk database"""
        nominal = float(data.get('nominal'))
        metodeId = data.get('metode_id')
        campaignId = data.get('campaign_id')

        # Get metode pembayaran DANA
        if not metodeId:
            metode = self.paymentModel.findByPaymentType('emoney', 'DANA')
            metodeId = metode['id'] if metode else 2
        else:
            metode = self.paymentModel.findById(metodeId)

        campaign = self.campaignModel.findById(campaignId) if campaignId else None
        fees = self._calculateFees(nominal, metode, campaign)

        orderId = f"ORDER-{uuid.uuid4().hex[:12].upper()}"
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
            'nama_lengkap': data.get('nama_lengkap'),
            'doa_muzaki': data.get('doa_muzaki', ''),
            'tipe_zakat': data.get('tipe_zakat', 'infak'),
            'tipe': data.get('tipe', 'perorangan'),
            'hamba_allah': data.get('hamba_allah', 'N'),
            'npwz': data.get('npwz', ''),
            'status': 'pending',
            'created_by': data.get('created_by', 'dana_api')
        }

    def _calculateFees(self, nominal, metode, campaign):
        """Hitung biaya operasional dan admin"""
        opsPercent = float(campaign.get('prosen_biayaoperasional', 0)) if campaign else 0
        opsFee = nominal * (opsPercent / 100)

        adminFee = 0
        if metode:
            adminRate = float(metode.get('biaya_admin', 0))
            if metode.get('payment_type') == 'emoney':
                adminFee = adminRate  # Flat fee untuk e-money
            elif 0 < adminRate < 1:
                adminFee = nominal * adminRate
            else:
                adminFee = adminRate

        return {
            'ops': opsFee,
            'ops_percent': opsPercent,
            'admin': adminFee,
            'net': nominal - opsFee,
            'total': nominal + adminFee
        }

    def applyOtt(self, data):
        """
        Apply OTT (One Time Token) untuk pembayaran
        Diperlukan sebelum user redirect ke halaman DANA
        """
        try:
            accessToken = data.get('access_token')
            orderId = data.get('order_id')

            if not accessToken or not orderId:
                return Response.error("Access token dan order_id wajib diisi", 400)

            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            if not donation.get('dana_reference_no'):
                return Response.error("Order belum dibuat di DANA", 400)

            if DANA_SDK_AVAILABLE:
                return self._applyOttWithSDK(donation, accessToken)
            else:
                return self._applyOttFallback(donation, accessToken)

        except Exception as e:
            return Response.error(f"Apply OTT gagal: {str(e)}", 500)

    def _applyOttWithSDK(self, donation, accessToken):
        """Apply OTT menggunakan DANA SDK"""
        try:
            self._initDanaClient()

            request_data = {
                "partnerReferenceNo": donation.get('partner_reference_no'),
                "originalReferenceNo": donation.get('dana_reference_no'),
                "merchantId": self.merchantId
            }

            response = dana_ipg.apply_ott(request_data, access_token=accessToken)

            self.logApiCall('dana_ipg.apply_ott', 'POST', request_data,
                           200, response, donation['order_id'])

            if response.get('responseCode') in ['2005300', '00']:
                ottToken = response.get('ott') or response.get('ottToken')
                if ottToken:
                    self.donationModel.updateOttToken(donation['order_id'], ottToken)

                return Response.success(data={
                    "orderId": donation['order_id'],
                    "ottToken": ottToken,
                    "webRedirectUrl": donation.get('dana_web_redirect_url')
                }, message="OTT berhasil didapatkan")
            else:
                return Response.error(
                    f"DANA Error: {response.get('responseMessage')}",
                    400
                )

        except Exception as e:
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _applyOttFallback(self, donation, accessToken):
        """Apply OTT tanpa SDK"""
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

        requestBody = {
            "partnerReferenceNo": donation.get('partner_reference_no'),
            "originalReferenceNo": donation.get('dana_reference_no'),
            "merchantId": self.merchantId
        }

        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/get-auth-code"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "Authorization": f"Bearer {accessToken}"
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            self.logApiCall(url, 'POST', requestBody, response.status_code,
                           result, donation['order_id'])

            if response.status_code == 200:
                ottToken = result.get('ott') or result.get('ottToken')
                if ottToken:
                    self.donationModel.updateOttToken(donation['order_id'], ottToken)

                return Response.success(data={
                    "orderId": donation['order_id'],
                    "ottToken": ottToken
                }, message="OTT berhasil didapatkan")
            else:
                return Response.error(f"DANA Error: {result.get('responseMessage')}", 400)

        except Exception as e:
            return Response.error(f"Request failed: {str(e)}", 500)

    def queryPayment(self, orderId):
        """Query status pembayaran dari DANA"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            if DANA_SDK_AVAILABLE:
                return self._queryPaymentWithSDK(donation)
            else:
                return self._queryPaymentFallback(donation)

        except Exception as e:
            return Response.error(f"Query payment gagal: {str(e)}", 500)

    def _queryPaymentWithSDK(self, donation):
        """Query payment menggunakan DANA SDK"""
        try:
            self._initDanaClient()

            request_data = {
                "originalPartnerReferenceNo": donation.get('partner_reference_no'),
                "originalReferenceNo": donation.get('dana_reference_no'),
                "merchantId": self.merchantId
            }

            response = dana_ipg.query_payment(request_data)

            self.logApiCall('dana_ipg.query_payment', 'POST', request_data,
                           200, response, donation['order_id'])

            danaStatus = response.get('latestTransactionStatus') or response.get('status')
            if danaStatus:
                self.donationModel.updateDanaStatusRef(
                    donation['order_id'],
                    donation.get('dana_reference_no'),
                    danaStatus
                )

            return Response.success(data={
                "orderId": donation['order_id'],
                "danaStatus": danaStatus,
                "internalStatus": donation.get('status'),
                "amount": response.get('amount'),
                "paidTime": response.get('paidTime')
            })

        except Exception as e:
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _queryPaymentFallback(self, donation):
        """Query payment tanpa SDK"""
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

        requestBody = {
            "originalPartnerReferenceNo": donation.get('partner_reference_no'),
            "originalReferenceNo": donation.get('dana_reference_no'),
            "merchantId": self.merchantId
        }

        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/debit/status"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            self.logApiCall(url, 'POST', requestBody, response.status_code,
                           result, donation['order_id'])

            danaStatus = result.get('latestTransactionStatus') or result.get('status')
            if danaStatus:
                self.donationModel.updateDanaStatusRef(
                    donation['order_id'],
                    donation.get('dana_reference_no'),
                    danaStatus
                )

            return Response.success(data={
                "orderId": donation['order_id'],
                "danaStatus": danaStatus,
                "internalStatus": donation.get('status'),
                "amount": result.get('amount')
            })

        except Exception as e:
            return Response.error(f"Request failed: {str(e)}", 500)

    def cancelOrder(self, orderId, reason='User cancelled'):
        """Cancel order yang belum dibayar"""
        try:
            donation = self.donationModel.findByOrderId(orderId)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            if donation.get('status') == 'berhasil':
                return Response.error("Order yang sudah dibayar tidak bisa dibatalkan", 400)

            # Update status lokal
            self.donationModel.updateStatus(orderId, 'cancelled')

            # TODO: Call DANA cancel API jika diperlukan

            return Response.success(message="Order berhasil dibatalkan")

        except Exception as e:
            return Response.error(f"Cancel order gagal: {str(e)}", 500)

    def webhook(self, data, signature=None):
        """
        Handle webhook dari DANA untuk update status pembayaran

        DANA akan kirim notifikasi ke endpoint ini ketika status pembayaran berubah
        """
        try:
            self.logApiCall('/webhook', 'POST', data, 200, None,
                           data.get('originalPartnerReferenceNo'))

            # Validate signature jika ada (recommended)
            if signature:
                if not self._verifyWebhookSignature(data, signature):
                    return Response.error("Invalid signature", 401)

            partnerRef = data.get('originalPartnerReferenceNo')
            danaRef = data.get('originalReferenceNo')
            status = data.get('latestTransactionStatus') or data.get('status')

            if not partnerRef:
                return Response.error("Missing partner reference", 400)

            donation = self.donationModel.findByPartnerRefNo(partnerRef)
            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            # Update status
            self.donationModel.updateDanaStatusRef(donation['order_id'], danaRef, status)

            # Sync ke SIMBA jika sukses
            if status == 'SUCCESS':
                self._syncToSimba(donation)

            # Response sesuai format DANA
            return Response.success(data={
                "responseCode": "2005500",
                "responseMessage": "Successful"
            })

        except Exception as e:
            return Response.error(f"Webhook gagal: {str(e)}", 500)

    def _verifyWebhookSignature(self, data, signature):
        """Verifikasi signature webhook dari DANA"""
        # TODO: Implement dengan public key DANA
        return True

    def _syncToSimba(self, donation):
        """Sync transaksi sukses ke SIMBA"""
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
