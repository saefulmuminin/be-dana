from src.models.base_model import BaseModel
from datetime import datetime

class DonationModel(BaseModel):
    """
    Model untuk tabel adm_campaign_donasi
    Digunakan untuk transaksi donasi termasuk via DANA payment
    """
    table_name = "adm_campaign_donasi"

    # Mapping status internal ke status database
    STATUS_MAP = {
        'pending': 'belum',
        'processing': 'menunggu',
        'success': 'berhasil',
        'failed': 'dibatalkan',
        'cancelled': 'dibatalkan',
        'expired': 'dibatalkan'
    }

    # Reverse mapping
    STATUS_MAP_REVERSE = {
        'belum': 'pending',
        'menunggu': 'processing',
        'berhasil': 'success',
        'dibatalkan': 'failed'
    }

    def create(self, data):
        """
        Insert donasi baru ke database
        """
        required_fields = ['nominal', 'metode_id', 'campaign_id', 'email']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required")

        checksum = self.generateChecksum(str(data.get('email')) + str(data.get('nominal')))
        uuid_val = self.generateUuid()

        # Map internal status ke DB status
        internal_status = data.get('status', 'pending')
        db_status = self.STATUS_MAP.get(internal_status, 'belum')

        # Calculate total_bayar
        nominal = float(data.get('nominal', 0))
        biaya_admin = float(data.get('biaya_admin', 0))
        total_bayar = nominal + biaya_admin

        with self.conn.cursor() as cursor:
            sql = f"""
                INSERT INTO {self.table_name}
                (uuid, checksum, order_id, partner_reference_no, campaign_id, muzaki_id,
                 metode_id, tipe_zakat, tipe, nama_lengkap, email, npwz, doa_muzaki,
                 nominal, prosen_biayaoperasional, biayaoperasional, biaya_admin,
                 donasi, donasi_net, total_bayar, hamba_allah, status, tgl_donasi,
                 is_active, is_delete, created_by, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                uuid_val,
                checksum,
                data.get('order_id'),
                data.get('partner_reference_no'),
                data.get('campaign_id'),
                data.get('muzaki_id'),
                data.get('metode_id'),
                data.get('tipe_zakat', 'infak'),
                data.get('tipe', 'perorangan'),
                data.get('nama_lengkap'),
                data.get('email'),
                data.get('npwz', ''),
                data.get('doa_muzaki', ''),
                nominal,
                data.get('prosen_biayaoperasional', 0),
                data.get('biaya_operasional', 0),
                biaya_admin,
                nominal,  # donasi = nominal
                data.get('donasi_net', nominal),
                total_bayar,
                data.get('hamba_allah', 'N'),
                db_status,
                data.get('tgl_donasi', datetime.now()),
                'Y',
                'N',
                data.get('created_by', 'system'),
                datetime.now()
            ))
            self.conn.commit()
            return cursor.lastrowid

    def findByOrderId(self, orderId):
        """
        Cari donasi berdasarkan order_id
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE order_id = %s AND is_delete = 'N'"
            cursor.execute(sql, (orderId,))
            result = cursor.fetchone()
            if result:
                result['status_internal'] = self.STATUS_MAP_REVERSE.get(result.get('status'), result.get('status'))
            return result

    def findByPartnerRefNo(self, partnerReferenceNo):
        """
        Cari donasi berdasarkan partner_reference_no
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT * FROM {self.table_name}
                WHERE partner_reference_no = %s AND is_delete = 'N'
            """
            cursor.execute(sql, (partnerReferenceNo,))
            result = cursor.fetchone()
            if result:
                result['status_internal'] = self.STATUS_MAP_REVERSE.get(result.get('status'), result.get('status'))
            return result

    def findById(self, id):
        """
        Cari donasi berdasarkan ID
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            if result:
                result['status_internal'] = self.STATUS_MAP_REVERSE.get(result.get('status'), result.get('status'))
            return result

    def updateStatus(self, orderId, status):
        """
        Update status donasi
        status: 'pending', 'processing', 'success', 'failed', 'cancelled'
        """
        db_status = self.STATUS_MAP.get(status, status)
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET status = %s, updated_date = %s, updated_by = 'system'
                WHERE order_id = %s
            """
            cursor.execute(sql, (db_status, datetime.now(), orderId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateDanaRefs(self, orderId, referenceNo, webRedirectUrl):
        """
        Update DANA reference setelah create order berhasil
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET dana_reference_no = %s, dana_web_redirect_url = %s, updated_date = %s
                WHERE order_id = %s
            """
            cursor.execute(sql, (referenceNo, webRedirectUrl, datetime.now(), orderId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateDanaStatusRef(self, orderId, referenceNo, danaStatus):
        """
        Update status dari DANA webhook
        """
        # Map DANA status ke internal status
        status_map = {
            'SUCCESS': 'berhasil',
            'FAILED': 'dibatalkan',
            'PENDING': 'menunggu',
            'CANCELLED': 'dibatalkan'
        }
        db_status = status_map.get(danaStatus, 'menunggu')
        dana_paid_at = datetime.now() if danaStatus == 'SUCCESS' else None

        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET dana_reference_no = %s, dana_status = %s, status = %s,
                    dana_paid_at = %s, updated_date = %s
                WHERE order_id = %s
            """
            cursor.execute(sql, (referenceNo, danaStatus, db_status, dana_paid_at, datetime.now(), orderId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateOttToken(self, orderId, ottToken):
        """
        Simpan OTT token untuk transaksi
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET dana_ott_token = %s, updated_date = %s
                WHERE order_id = %s
            """
            cursor.execute(sql, (ottToken, datetime.now(), orderId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateNpwz(self, orderId, npwz):
        """
        Update NPWZ setelah register ke SIMBA
        """
        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET npwz = %s, updated_date = %s WHERE order_id = %s"
            cursor.execute(sql, (npwz, datetime.now(), orderId))
            self.conn.commit()
            return cursor.rowcount > 0

    def getHistoryByEmail(self, email, limit=50, offset=0):
        """
        Ambil history donasi berdasarkan email
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT d.*, c.name as campaign_name, c.url_fotoutama as campaign_image,
                       m.name as metode_name, m.url_gambar as metode_image
                FROM {self.table_name} d
                LEFT JOIN adm_campaign c ON d.campaign_id = c.id
                LEFT JOIN ref_metode_pembayaran m ON d.metode_id = m.id
                WHERE d.email = %s AND d.is_delete = 'N'
                ORDER BY d.created_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (email, limit, offset))
            results = cursor.fetchall()
            # Add internal status mapping
            for r in results:
                r['status_internal'] = self.STATUS_MAP_REVERSE.get(r.get('status'), r.get('status'))
            return results

    def getHistoryByMuzakiId(self, muzakiId, limit=50, offset=0):
        """
        Ambil history donasi berdasarkan muzaki_id
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT d.*, c.name as campaign_name, c.url_fotoutama as campaign_image,
                       m.name as metode_name, m.url_gambar as metode_image
                FROM {self.table_name} d
                LEFT JOIN adm_campaign c ON d.campaign_id = c.id
                LEFT JOIN ref_metode_pembayaran m ON d.metode_id = m.id
                WHERE d.muzaki_id = %s AND d.is_delete = 'N'
                ORDER BY d.created_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (muzakiId, limit, offset))
            results = cursor.fetchall()
            for r in results:
                r['status_internal'] = self.STATUS_MAP_REVERSE.get(r.get('status'), r.get('status'))
            return results

    def countByEmail(self, email):
        """
        Hitung total donasi berdasarkan email
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'berhasil' THEN nominal ELSE 0 END) as total_donasi
                FROM {self.table_name}
                WHERE email = %s AND is_delete = 'N'
            """
            cursor.execute(sql, (email,))
            return cursor.fetchone()
