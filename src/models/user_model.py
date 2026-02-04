from src.models.base_model import BaseModel
from datetime import datetime
import time

class UserModel(BaseModel):
    """
    Model untuk tabel users
    Menyimpan data user termasuk DANA OAuth tokens
    """
    table_name = "users"

    def create(self, data):
        """
        Buat user baru
        Mendukung kolom DANA OAuth yang baru ditambahkan
        """
        email = data.get('email')
        if not email:
            raise ValueError("Email is required")

        with self.conn.cursor() as cursor:
            sql = f"""
                INSERT INTO {self.table_name}
                (ip_address, username, email, password, full_name, tipe, handphone,
                 muzaki_id, dana_access_token, dana_refresh_token, dana_token_expires_at,
                 dana_external_id, dana_user_id, dana_linked_at, created_on, active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data.get('ip_address', '0.0.0.0'),
                data.get('username', email),
                email,
                data.get('password', ''),
                data.get('full_name', data.get('name', '')),
                data.get('tipe', 'user'),
                data.get('handphone', ''),
                data.get('muzaki_id'),
                data.get('dana_access_token'),
                data.get('dana_refresh_token'),
                data.get('dana_token_expires_at'),
                data.get('dana_external_id'),
                data.get('dana_user_id'),
                data.get('dana_linked_at'),
                int(time.time()),  # created_on sebagai unix timestamp
                1  # active
            ))
            self.conn.commit()
            return cursor.lastrowid

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
