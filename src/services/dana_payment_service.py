"""
DANA Mini Program Payment Service
Untuk integrasi pembayaran di DANA Mini App

Flow Mini Program Payment:
1. User isi form donasi di mini app
2. Mini app call backend /create-order -> backend return orderId
3. Mini app call my.tradePay(tradeNO: orderId)
4. DANA SDK handle pembayaran
5. DANA kirim webhook ke backend untuk update status

Catatan: my.tradePay menangani pembayaran langsung,
backend hanya perlu menyimpan order dan menerima webhook.
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

            # Save to database
            donationId = self.donationModel.create(orderData)
            if not donationId:
                return Response.error("Gagal menyimpan order", 500)

            self.logApiCall('/create-order', 'POST', data, 200,
                           {'order_id': orderData['order_id']},
                           orderData['order_id'])

            return Response.success(data={
                "orderId": orderData['order_id'],
                "partnerReferenceNo": orderData['partner_reference_no'],
                "amount": int(orderData['total_bayar']),
                "nominal": int(orderData['nominal']),
                "biayaAdmin": int(orderData['biaya_admin']),
                "status": "pending",
                "message": "Order berhasil dibuat. Gunakan orderId untuk my.tradePay()"
            }, message="Order berhasil dibuat")

        except Exception as e:
            self.logApiCall('/create-order', 'POST', data, 500, None, error=str(e))
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
        metodeId = data.get('metode_id')

        # Get metode pembayaran DANA
        if not metodeId:
            metode = self.paymentModel.findByPaymentType('emoney', 'DANA')
            metodeId = metode['id'] if metode else 2
        else:
            metode = self.paymentModel.findById(metodeId)

        campaign = self.campaignModel.findById(campaignId) if campaignId else None
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
        opsPercent = float(campaign.get('prosen_biayaoperasional', 0)) if campaign else 0
        opsFee = nominal * (opsPercent / 100)

        adminFee = 0
        if metode:
            adminRate = float(metode.get('biaya_admin', 0))
            if metode.get('payment_type') == 'emoney':
                adminFee = adminRate
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

    def webhook(self, data, signature=None):
        """
        Handle webhook dari DANA untuk update status pembayaran

        DANA akan kirim notifikasi saat:
        - Pembayaran berhasil (SUCCESS)
        - Pembayaran gagal (FAILED)
        - Pembayaran expired (EXPIRED)
        """
        try:
            self.logApiCall('/webhook', 'POST', data, 200, None,
                           data.get('merchantTransId') or data.get('partnerReferenceNo'))

            # Extract data dari webhook
            orderId = data.get('merchantTransId') or data.get('originalPartnerReferenceNo')
            partnerRef = data.get('partnerReferenceNo') or data.get('originalPartnerReferenceNo')
            danaRef = data.get('referenceNo') or data.get('originalReferenceNo')
            status = data.get('status') or data.get('latestTransactionStatus')
            amount = data.get('amount', {}).get('value') if isinstance(data.get('amount'), dict) else data.get('amount')

            # Cari donation
            donation = None
            if orderId:
                donation = self.donationModel.findByOrderId(orderId)
            if not donation and partnerRef:
                donation = self.donationModel.findByPartnerRefNo(partnerRef)

            if not donation:
                return Response.error("Order tidak ditemukan", 404)

            # Map DANA status ke internal status
            internalStatus = self._mapDanaStatus(status)

            # Update database
            self.donationModel.updateDanaStatusRef(
                donation['order_id'],
                danaRef,
                internalStatus
            )

            # Sync ke SIMBA jika sukses
            if internalStatus == 'berhasil':
                self._syncToSimba(donation)

            # Response sesuai format DANA
            return Response.success(data={
                "responseCode": "2005500",
                "responseMessage": "Successful"
            })

        except Exception as e:
            self.logApiCall('/webhook', 'POST', data, 500, None, error=str(e))
            return Response.error(f"Webhook error: {str(e)}", 500)

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
        Handle finish payment callback dari DANA

        Endpoint ini dipanggil setelah user selesai di halaman DANA
        """
        orderId = data.get('orderId') or data.get('merchantTransId')
        resultCode = data.get('resultCode')
        resultStatus = data.get('resultStatus')

        if not orderId:
            return Response.success(data={
                "message": "Callback received",
                "resultCode": resultCode
            })

        donation = self.donationModel.findByOrderId(orderId)
        if not donation:
            return Response.success(data={
                "message": "Order not found",
                "orderId": orderId
            })

        # Map result code
        if resultCode == '9000':
            status = 'berhasil'
        elif resultCode == '6001':
            status = 'dibatalkan'
        else:
            status = 'pending'

        return Response.success(data={
            "orderId": orderId,
            "status": status,
            "resultCode": resultCode,
            "message": "Payment callback received"
        })
