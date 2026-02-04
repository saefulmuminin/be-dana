from src.utils.database import db
import uuid
import hashlib

class BaseModel:
    table_name = ""

    def __init__(self):
        self.conn = db.getConnection()

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
        self.conn.close()
