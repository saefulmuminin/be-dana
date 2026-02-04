import psycopg2
from psycopg2.extras import RealDictCursor
from src.config.config import Config

class Database:
    def __init__(self):
        # Gunakan SQLALCHEMY_DATABASE_URI dari Config
        self.database_url = Config.SQLALCHEMY_DATABASE_URI

    def getConnection(self):
        try:
            if not self.database_url or self.database_url.startswith("sqlite"):
                raise Exception("PostgreSQL DATABASE_URL is not set")

            return psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
        except Exception as e:
            print(f"Database Connection Error: {str(e)}")
            raise e

    def execute_query(self, query, params=None, fetch=True):
        """Helper method untuk execute query"""
        conn = None
        try:
            conn = self.getConnection()
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount

            cursor.close()
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_one(self, query, params=None):
        """Helper method untuk fetch single row"""
        conn = None
        try:
            conn = self.getConnection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()

# Singleton instance
db = Database()
