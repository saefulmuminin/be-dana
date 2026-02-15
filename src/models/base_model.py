from src.utils.database import db
import uuid
import hashlib

class BaseModel:
    table_name = ""

    def __init__(self):
        # Lazy connection - jangan connect saat init
        self._conn = None

    @property
    def conn(self):
        """Lazy database connection - hanya connect saat dibutuhkan, dan reconnect jika closed"""
        try:
            # Check if connection exists and is open
            # closed: 0 = valid, > 0 = closed/error
            if self._conn is None or self._conn.closed != 0:
                print(f"[DB] Reconnecting... (Old Status: {self._conn.closed if self._conn else 'None'})")
                self._conn = db.getConnection()
        except Exception as e:
            # Force reconnect on error checking status
            print(f"[DB] Connection check failed: {e}. Reconnecting...")
            self._conn = None # Reset
            try:
                self._conn = db.getConnection()
            except Exception as connectErr:
                print(f"[DB] Reconnection failed: {connectErr}")
                raise connectErr
            
        return self._conn

    def generateUuid(self):
        return str(uuid.uuid4())

    def generateChecksum(self, dataStr):
        return hashlib.sha256(dataStr.encode()).hexdigest()

    def findById(self, id):
        with self.conn.cursor() as cursor:
            sql = f"SELECT * FROM {self.table_name} WHERE id = %s AND is_delete = 'N'"
            cursor.execute(sql, (id,))
            return cursor.fetchone()

    def softDelete(self, id):
        with self.conn.cursor() as cursor:
            sql = f"UPDATE {self.table_name} SET is_delete = 'Y' WHERE id = %s"
            cursor.execute(sql, (id,))
            self.conn.commit()
            return cursor.rowcount > 0

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
