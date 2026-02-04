from src.models.muzaki_model import MuzakiModel
from src.models.donation_model import DonationModel
from src.models.user_model import UserModel
from src.utils.response import Response


class UserService:
    """
    Service untuk operasi user: profile, transaction history, dll
    """

    def __init__(self):
        self.muzakiModel = MuzakiModel()
        self.donationModel = DonationModel()
        self.userModel = UserModel()

    def getProfile(self, userId=None, email=None, muzakiId=None):
        """
        Ambil profil user/muzaki

        Args:
            userId: ID user dari JWT token
            email: Email user (fallback)
            muzakiId: ID muzaki langsung
        """
        try:
            # Prioritas: muzakiId > userId > email
            if muzakiId:
                muzaki = self.muzakiModel.findById(muzakiId)
            elif userId:
                user = self.userModel.findById(userId)
                if user and user.get('muzaki_id'):
                    muzaki = self.muzakiModel.findById(user['muzaki_id'])
                elif user and user.get('email'):
                    muzaki = self.muzakiModel.findByEmail(user['email'])
                else:
                    muzaki = None
            elif email:
                muzaki = self.muzakiModel.findByEmail(email)
            else:
                return Response.error("User identifier required", 400)

            if not muzaki:
                return Response.error("Profil tidak ditemukan", 404)

            # Get donation stats
            stats = self.muzakiModel.getTotalDonasi(muzaki['id'])

            return Response.success(data={
                "id": muzaki['id'],
                "nama": muzaki.get('nama'),
                "email": muzaki.get('email'),
                "handphone": muzaki.get('handphone'),
                "nik": muzaki.get('nik'),
                "npwz": muzaki.get('npwz'),
                "npwp": muzaki.get('npwp'),
                "alamat": muzaki.get('alamat'),
                "tgl_lahir": str(muzaki.get('tgl_lahir')) if muzaki.get('tgl_lahir') else None,
                "jenis_kelamin": muzaki.get('jenis_kelamin'),
                "foto": muzaki.get('foto'),
                "tipe": muzaki.get('tipe'),
                "stats": {
                    "jumlah_donasi": stats.get('jumlah_donasi', 0) if stats else 0,
                    "total_donasi": float(stats.get('total_donasi', 0)) if stats else 0
                }
            })

        except Exception as e:
            return Response.error(f"Gagal mengambil profil: {str(e)}", 500)

    def updateProfile(self, muzakiId, data):
        """
        Update profil muzaki
        """
        try:
            if not muzakiId:
                return Response.error("Muzaki ID required", 400)

            muzaki = self.muzakiModel.findById(muzakiId)
            if not muzaki:
                return Response.error("Profil tidak ditemukan", 404)

            success = self.muzakiModel.updateProfile(muzakiId, data)
            if success:
                return Response.success(message="Profil berhasil diupdate")
            else:
                return Response.error("Tidak ada perubahan", 400)

        except Exception as e:
            return Response.error(f"Gagal update profil: {str(e)}", 500)

    def getTransactionHistory(self, userId=None, email=None, muzakiId=None, limit=50, offset=0):
        """
        Ambil history transaksi donasi

        Args:
            userId: ID user dari JWT token
            email: Email user (fallback)
            muzakiId: ID muzaki langsung
            limit: Jumlah data per halaman
            offset: Offset untuk paginasi
        """
        try:
            # Tentukan identifier untuk query
            if muzakiId:
                history = self.donationModel.getHistoryByMuzakiId(muzakiId, limit, offset)
            elif userId:
                user = self.userModel.findById(userId)
                if user and user.get('muzaki_id'):
                    history = self.donationModel.getHistoryByMuzakiId(user['muzaki_id'], limit, offset)
                elif user and user.get('email'):
                    history = self.donationModel.getHistoryByEmail(user['email'], limit, offset)
                else:
                    history = []
            elif email:
                history = self.donationModel.getHistoryByEmail(email, limit, offset)
            else:
                return Response.error("User identifier required", 400)

            # Format response
            formattedHistory = []
            for item in history:
                formattedHistory.append({
                    "id": item.get('id'),
                    "order_id": item.get('order_id'),
                    "campaign_name": item.get('campaign_name'),
                    "campaign_image": item.get('campaign_image'),
                    "nominal": float(item.get('nominal', 0)),
                    "biaya_admin": float(item.get('biaya_admin', 0)),
                    "total_bayar": float(item.get('total_bayar', 0)),
                    "status": item.get('status_internal', item.get('status')),
                    "dana_status": item.get('dana_status'),
                    "tipe_zakat": item.get('tipe_zakat'),
                    "metode_name": item.get('metode_name'),
                    "metode_image": item.get('metode_image'),
                    "tgl_donasi": str(item.get('tgl_donasi')) if item.get('tgl_donasi') else None,
                    "created_date": str(item.get('created_date')) if item.get('created_date') else None
                })

            return Response.success(data={
                "transactions": formattedHistory,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "count": len(formattedHistory)
                }
            })

        except Exception as e:
            return Response.error(f"Gagal mengambil history: {str(e)}", 500)

    def getTransactionDetail(self, orderId, userId=None):
        """
        Ambil detail transaksi donasi

        Args:
            orderId: Order ID atau ID transaksi
            userId: ID user untuk validasi kepemilikan (optional)
        """
        try:
            # Cari berdasarkan order_id dulu
            detail = self.donationModel.findByOrderId(orderId)

            # Jika tidak ditemukan, coba cari berdasarkan ID
            if not detail:
                try:
                    detailId = int(orderId)
                    detail = self.donationModel.findById(detailId)
                except ValueError:
                    pass

            if not detail:
                return Response.error("Transaksi tidak ditemukan", 404)

            # Validasi kepemilikan jika userId diberikan
            if userId:
                user = self.userModel.findById(userId)
                if user:
                    userEmail = user.get('email')
                    userMuzakiId = user.get('muzaki_id')

                    # Cek apakah transaksi milik user ini
                    if detail.get('email') != userEmail and detail.get('muzaki_id') != userMuzakiId:
                        return Response.error("Tidak memiliki akses ke transaksi ini", 403)

            return Response.success(data={
                "id": detail.get('id'),
                "order_id": detail.get('order_id'),
                "partner_reference_no": detail.get('partner_reference_no'),
                "dana_reference_no": detail.get('dana_reference_no'),
                "campaign_id": detail.get('campaign_id'),
                "campaign_name": detail.get('campaign_name'),
                "nama_lengkap": detail.get('nama_lengkap'),
                "email": detail.get('email'),
                "npwz": detail.get('npwz'),
                "nominal": float(detail.get('nominal', 0)),
                "biaya_admin": float(detail.get('biaya_admin', 0)),
                "biaya_operasional": float(detail.get('biayaoperasional', 0)),
                "donasi_net": float(detail.get('donasi_net', 0)),
                "total_bayar": float(detail.get('total_bayar', 0)),
                "status": detail.get('status_internal', detail.get('status')),
                "dana_status": detail.get('dana_status'),
                "tipe_zakat": detail.get('tipe_zakat'),
                "tipe": detail.get('tipe'),
                "hamba_allah": detail.get('hamba_allah'),
                "doa_muzaki": detail.get('doa_muzaki'),
                "tgl_donasi": str(detail.get('tgl_donasi')) if detail.get('tgl_donasi') else None,
                "dana_paid_at": str(detail.get('dana_paid_at')) if detail.get('dana_paid_at') else None,
                "dana_web_redirect_url": detail.get('dana_web_redirect_url'),
                "created_date": str(detail.get('created_date')) if detail.get('created_date') else None
            })

        except Exception as e:
            return Response.error(f"Gagal mengambil detail: {str(e)}", 500)

    def sendHistoryEmail(self, email, muzakiId=None):
        """
        Kirim email history donasi ke user
        TODO: Implement email sending
        """
        try:
            # Get history
            if muzakiId:
                history = self.donationModel.getHistoryByMuzakiId(muzakiId)
            else:
                history = self.donationModel.getHistoryByEmail(email)

            if not history:
                return Response.error("Tidak ada history donasi", 404)

            # TODO: Implement email sending logic
            # - Generate PDF/HTML report
            # - Send via email service

            return Response.success(message=f"History donasi akan dikirim ke {email}")

        except Exception as e:
            return Response.error(f"Gagal mengirim email: {str(e)}", 500)
