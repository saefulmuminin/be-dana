from src.models.base_model import BaseModel


class RefKantorModel(BaseModel):
    """
    Model untuk tabel ref_kantor (kantor/institusi zakat)
    """
    table_name = "ref_kantor"

    def findById(self, id):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_active = 'Y' AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()

    def findAllOffices(self, tipe=None):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 'Y' AND is_delete = 'N'"
            if tipe:
                sql += " AND tipe = %s"
                cursor.execute(sql, (tipe,))
            else:
                cursor.execute(sql)
            return cursor.fetchall()

    def findByKode(self, kode):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE kode_institusi = %s AND is_active = 'Y' AND is_delete = 'N'"
            cursor.execute(sql, (kode,))
            return cursor.fetchone()


class RefPaymentModel(BaseModel):
    """
    Model untuk tabel ref_metode_pembayaran
    """
    table_name = "ref_metode_pembayaran"

    def findById(self, id):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_active = 'Y' AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()

    def findByPaymentType(self, paymentType, bank=None):
        """
        Cari metode pembayaran berdasarkan payment_type dan bank
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE payment_type = %s AND is_active = 'Y' AND is_delete = 'N'"
            params = [paymentType]
            if bank:
                sql += " AND bank = %s"
                params.append(bank)
            cursor.execute(sql, tuple(params))
            return cursor.fetchone()

    def findAll(self):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 'Y' AND is_delete = 'N' ORDER BY order_list"
            cursor.execute(sql)
            return cursor.fetchall()

    def getGroupedPayments(self):
        """
        Ambil metode pembayaran yang dikelompokkan berdasarkan kelompok
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE is_active = 'Y' AND is_delete = 'N' ORDER BY order_list"
            cursor.execute(sql)
            results = cursor.fetchall()

            grouped = {}
            for row in results:
                group = row.get('kelompok', 'Other')
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(row)
            return grouped


class RefCampaignModel(BaseModel):
    """
    Model untuk tabel adm_campaign
    """
    table_name = "adm_campaign"

    def findById(self, id):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()

    def findBySlug(self, slug):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE slug = %s AND is_delete = 'N' AND is_active = 'Y'"
            cursor.execute(sql, (slug,))
            return cursor.fetchone()

    def findActive(self, limit=20, offset=0):
        """
        Ambil campaign yang aktif
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT * FROM {self.table_name}
                WHERE is_active = 'Y' AND is_delete = 'N' AND status = 'publish'
                ORDER BY prioritas DESC, created_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (limit, offset))
            return cursor.fetchall()

    def findByTipe(self, tipe, limit=20, offset=0):
        """
        Ambil campaign berdasarkan tipe (zakat/infak)
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                SELECT * FROM {self.table_name}
                WHERE tipe = %s AND is_active = 'Y' AND is_delete = 'N' AND status = 'publish'
                ORDER BY prioritas DESC, created_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (tipe, limit, offset))
            return cursor.fetchall()
