from src.models.base_model import BaseModel
from datetime import datetime
import time

class UserModel(BaseModel):
    """
    Model untuk tabel adm_user
    Menyimpan data user termasuk DANA OAuth tokens
    """
    table_name = "users"

    def create(self, data):
        """
        Buat user baru
        Mendukung kolom DANA OAuth yang baru ditambahkan
        """
        email = data.get('email')
        # Email is now optional for Seamless Login (will be filled later)
        # if not email:
        #     raise ValueError("Email is required")

        with self.conn.cursor() as cursor:
            sql = f"""
                INSERT INTO {self.table_name}
                (email, password, full_name, tipe, handphone, muzaki_id,
                 dana_access_token, dana_refresh_token, dana_token_expires_at,
                 dana_external_id, dana_user_id, dana_linked_at, 
                 active, created_on, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            cursor.execute(sql, (
                email,
                data.get('password', ''),
                data.get('full_name', data.get('name', data.get('nama', ''))),
                data.get('tipe', 'user'),
                data.get('handphone', data.get('no_hp', '')),
                data.get('muzaki_id'),
                data.get('dana_access_token'),
                data.get('dana_refresh_token'),
                data.get('dana_token_expires_at'),
                data.get('dana_external_id'),
                data.get('dana_user_id'),
                data.get('dana_linked_at'),
                1,  # active (1=active)
                int(time.time()),  # created_on (timestamp)
                data.get('ip_address', '127.0.0.1')
            ))
            result = cursor.fetchone()
            self.conn.commit()
            return result['id'] if result else None

    def findById(self, userId):
        """
        Cari user berdasarkan ID
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s"
            cursor.execute(sql, (userId,))
            return cursor.fetchone()

    def findByEmail(self, email):
        """
        Cari user berdasarkan email
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()

    def findByEmailAndType(self, email, tipe):
        """
        Cari user berdasarkan email dan tipe
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE email = %s AND tipe = %s"
            cursor.execute(sql, (email, tipe))
            return cursor.fetchone()

    def findByDanaExternalId(self, externalId):
        """
        Cari user berdasarkan DANA external_id
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE dana_external_id = %s"
            cursor.execute(sql, (externalId,))
            return cursor.fetchone()

    def findByPhone(self, phone):
        """
        Cari user berdasarkan nomor HP
        """
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE handphone = %s"
            cursor.execute(sql, (phone,))
            return cursor.fetchone()

    def updateExternalId(self, userId, externalId):
        """
        Update external_id untuk user (Mapped to dana_external_id)
        """
        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET dana_external_id = %s WHERE id = %s"
            cursor.execute(sql, (externalId, userId))
            self.conn.commit()
            return cursor.rowcount > 0

    def exists(self, email, tipe):
        """
        Cek apakah user dengan email dan tipe sudah ada
        """
        return self.findByEmailAndType(email, tipe) is not None

    def updateDanaToken(self, userId, data):
        """
        Update DANA OAuth tokens untuk user
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET dana_access_token = %s,
                    dana_refresh_token = %s,
                    dana_token_expires_at = %s,
                    dana_external_id = COALESCE(%s, dana_external_id),
                    dana_user_id = COALESCE(%s, dana_user_id),
                    dana_linked_at = COALESCE(dana_linked_at, %s)
                WHERE id = %s
            """
            cursor.execute(sql, (
                data.get('dana_access_token'),
                data.get('dana_refresh_token'),
                data.get('dana_token_expires_at'),
                data.get('dana_external_id'),
                data.get('dana_user_id'),
                datetime.now(),
                userId
            ))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateMuzakiId(self, userId, muzakiId):
        """
        Link user dengan muzaki
        """
        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET muzaki_id = %s WHERE id = %s"
            cursor.execute(sql, (muzakiId, userId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateLastLogin(self, userId):
        """
        Update waktu last login
        """
        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET last_login = %s WHERE id = %s"
            cursor.execute(sql, (int(time.time()), userId))
            self.conn.commit()
            return cursor.rowcount > 0

    def updateEmail(self, userId, email):
        """
        Update email user
        """
        try:
            with self.conn.cursor() as cursor:
                sql = f"UPDATE {self.table_name} SET email = %s WHERE id = %s"
                cursor.execute(sql, (email, userId))
                self.conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB] Update email failed: {e}")
            self.conn.rollback()
            return False

    def getDanaAccessToken(self, userId):
        """
        Ambil DANA access token jika masih valid
        """
        user = self.findById(userId)
        if not user:
            return None

        expiresAt = user.get('dana_token_expires_at')
        if expiresAt and datetime.now() > expiresAt:
            return None  # Token expired

        return user.get('dana_access_token')

    def clearDanaData(self, userId):
        """
        Hapus data binding DANA (Unbind/Logout)
        """
        with self.conn.cursor() as cursor:
            sql = f"""
                UPDATE {self.table_name}
                SET dana_access_token = NULL,
                    dana_refresh_token = NULL,
                    dana_token_expires_at = NULL,
                    dana_linked_at = NULL
                WHERE id = %s
            """
            cursor.execute(sql, (userId,))
            self.conn.commit()
            return cursor.rowcount > 0
