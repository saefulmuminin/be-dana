"""
Model untuk logging transaksi DANA
Menyimpan semua transaksi DANA (pending, success, failed, cancelled) untuk tracking
"""

from src.config.database import Database
import json
from datetime import datetime


class LogDanaTransactionModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = 'log_dana_transaction'

    def create(self, data):
        """
        Simpan log transaksi DANA
        
        Args:
            data: Dictionary dengan field:
                - order_id (required)
                - partner_reference_no
                - dana_reference_no
                - merchant_id
                - amount
                - currency
                - status
                - status_desc
                - created_time
                - finished_time
                - paid_time
                - payment_method
                - user_id
                - email
                - phone
                - raw_payload (dict/object, akan di-convert ke JSON)
        
        Returns:
            ID dari record yang dibuat, atau None jika gagal
        """
        try:
            with self.conn.cursor() as cursor:
                # Convert raw_payload to JSON string if it's a dict
                raw_payload = data.get('raw_payload')
                if raw_payload and isinstance(raw_payload, dict):
                    raw_payload = json.dumps(raw_payload)
                
                sql = f"""
                    INSERT INTO {self.table_name} (
                        order_id, partner_reference_no, dana_reference_no, merchant_id,
                        amount, currency, status, status_desc,
                        created_time, finished_time, paid_time, payment_method,
                        user_id, email, phone, raw_payload
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """
                
                cursor.execute(sql, (
                    data.get('order_id'),
                    data.get('partner_reference_no'),
                    data.get('dana_reference_no'),
                    data.get('merchant_id'),
                    data.get('amount'),
                    data.get('currency', 'IDR'),
                    data.get('status'),
                    data.get('status_desc'),
                    data.get('created_time'),
                    data.get('finished_time'),
                    data.get('paid_time'),
                    data.get('payment_method'),
                    data.get('user_id'),
                    data.get('email'),
                    data.get('phone'),
                    raw_payload
                ))
                
                result = cursor.fetchone()
                self.conn.commit()
                
                if result:
                    print(f"[LOG_DANA] Transaction logged: {data.get('order_id')}, Status: {data.get('status')}")
                    return result['id']
                return None
                
        except Exception as e:
            print(f"[LOG_DANA] Error logging transaction: {e}")
            self.conn.rollback()
            return None

    def findByOrderId(self, order_id):
        """
        Cari log transaksi berdasarkan order_id
        
        Args:
            order_id: Order ID untuk dicari
        
        Returns:
            List of transaction logs (bisa lebih dari 1 jika ada update status)
        """
        try:
            with self.conn.cursor() as cursor:
                sql = f"""
                    SELECT * FROM {self.table_name}
                    WHERE order_id = %s
                    ORDER BY webhook_received_at DESC
                """
                cursor.execute(sql, (order_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"[LOG_DANA] Error finding transaction: {e}")
            return []

    def findLatestByOrderId(self, order_id):
        """
        Cari log transaksi terbaru berdasarkan order_id
        
        Args:
            order_id: Order ID untuk dicari
        
        Returns:
            Latest transaction log atau None
        """
        try:
            with self.conn.cursor() as cursor:
                sql = f"""
                    SELECT * FROM {self.table_name}
                    WHERE order_id = %s
                    ORDER BY webhook_received_at DESC
                    LIMIT 1
                """
                cursor.execute(sql, (order_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"[LOG_DANA] Error finding latest transaction: {e}")
            return None

    def updateStatus(self, order_id, status, status_desc, finished_time=None, paid_time=None):
        """
        Update status transaksi
        
        Args:
            order_id: Order ID
            status: Status baru
            status_desc: Deskripsi status
            finished_time: Waktu selesai (optional)
            paid_time: Waktu bayar (optional)
        
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            with self.conn.cursor() as cursor:
                sql = f"""
                    UPDATE {self.table_name}
                    SET status = %s,
                        status_desc = %s,
                        finished_time = %s,
                        paid_time = %s,
                        updated_date = CURRENT_TIMESTAMP
                    WHERE order_id = %s
                    AND id = (
                        SELECT id FROM {self.table_name}
                        WHERE order_id = %s
                        ORDER BY webhook_received_at DESC
                        LIMIT 1
                    )
                """
                cursor.execute(sql, (status, status_desc, finished_time, paid_time, order_id, order_id))
                self.conn.commit()
                
                print(f"[LOG_DANA] Status updated: {order_id} -> {status}")
                return True
                
        except Exception as e:
            print(f"[LOG_DANA] Error updating status: {e}")
            self.conn.rollback()
            return False

    def getRecentTransactions(self, limit=10):
        """
        Ambil transaksi terbaru
        
        Args:
            limit: Jumlah record yang diambil
        
        Returns:
            List of recent transactions
        """
        try:
            with self.conn.cursor() as cursor:
                sql = f"""
                    SELECT * FROM {self.table_name}
                    ORDER BY webhook_received_at DESC
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
                return cursor.fetchall()
        except Exception as e:
            print(f"[LOG_DANA] Error getting recent transactions: {e}")
            return []
