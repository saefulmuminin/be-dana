import pymysql
from src.config.config import Config

class Database:
    def __init__(self):
        self.host = Config.DB_HOST
        self.user = Config.DB_USER
        self.password = Config.DB_PASS
        self.dbName = Config.DB_NAME

    def getConnection(self):
        try:
            return pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.dbName,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=5
            )
        except Exception as e:
            print(f"Database Connection Error: {str(e)}")
            print(f"Details: host={self.host}, user={self.user}, db={self.dbName}")
            raise e

# Singleton instance idea or just class usage
db = Database()
