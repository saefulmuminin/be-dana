from src.models.base_model import BaseModel
from datetime import datetime

class MuzakiModel(BaseModel):
    """
    Model untuk tabel adm_muzaki
    Menyimpan data muzaki (donatur/pemberi zakat)
    """
    table_name = "adm_muzaki"

    def create(self, data):
        """
        Buat muzaki baru
        """
        email = data.get('email')
        nama = data.get('nama')

        if not email or not nama:
            raise ValueError("Email dan nama wajib diisi")

        with self.conn.cursor() as cursor:
            sql = f"""
                INSERT INTO {self.table_name}
                (tipe, kelompok, kode_institusi, nama, foto, nik, npwp, npwz, npwz_bg,
                 tgl_daftar, handphone, email, alamat, tgl_lahir, jenis_kelamin,
                 is_active, is_delete, created_by, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('tipe', 'perorangan'),
                data.get('kelompok'),
                data.get('kode_institusi', 'PUSAT'),
                nama,
                data.get('foto'),
                data.get('nik', ''),
                data.get('npwp', ''),
                data.get('npwz', ''),
                data.get('npwz_bg', ''),
                data.get('tgl_daftar', datetime.now().strftime('%Y-%m-%d')),
                data.get('handphone', ''),
                email,
                data.get('alamat', ''),
                data.get('tgl_lahir'),
                data.get('jenis_kelamin'),
                'Y',
                'N',
                data.get('created_by', 'system'),
                datetime.now()
            ))
            self.conn.commit()
            return cursor.lastrowid

    def findById(self, id):
        """
        Cari muzaki berdasarkan ID
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()

    def findByEmail(self, email):
        """
        Cari muzaki berdasarkan email
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE email = %s AND is_delete = 'N'"
            cursor.execute(sql, (email,))
            return cursor.fetchone()

    def findByNpwz(self, npwz):
        """
        Cari muzaki berdasarkan NPWZ
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE npwz = %s AND is_delete = 'N'"
            cursor.execute(sql, (npwz,))
            return cursor.fetchone()

    def findByHandphone(self, handphone):
        """
        Cari muzaki berdasarkan nomor HP
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE handphone = %s AND is_delete = 'N'"
            cursor.execute(sql, (handphone,))
            return cursor.fetchone()

    def updateProfile(self, id, data):
        """
        Update profil muzaki
        """
        allowed_fields = ['nama', 'nik', 'npwp', 'handphone', 'alamat',
                          'tgl_lahir', 'jenis_kelamin', 'foto', 'email']
        updates = []
        values = []

        for field in allowed_fields:
            if field in data and data[field] is not None:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return False

        updates.append("updated_by = %s")
        values.append(data.get('updated_by', 'system'))
        updates.append("updated_date = %s")
        values.append(datetime.now())

        values.append(id)

        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateNpwz(self, id, npwz, npwzBg=''):
        """
        Update NPWZ muzaki setelah registrasi ke SIMBA
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET npwz = %s, npwz_bg = %s, updated_date = %s
                WHERE id = %s
            """
            cursor.execute(sql, (npwz, npwzBg, datetime.now(), id))
            self.conn.commit()
            return cursor.rowcount > 0

    def getTotalDonasi(self, muzakiId):
        """
        Hitung total donasi dari muzaki
        """
        with self.conn.cursor() as cursor:
            sql = """
                SELECT COUNT(*) as jumlah_donasi,
                       COALESCE(SUM(CASE WHEN status = 'berhasil' THEN nominal ELSE 0 END), 0) as total_donasi
                FROM adm_campaign_donasi
                WHERE muzaki_id = %s AND is_delete = 'N'
            """
            cursor.execute(sql, (muzakiId,))
            return cursor.fetchone()
