from src.utils.response import Response

class HealthService:
    def checkDatabase(self):
        try:
            from src.utils.database import db
            conn = db.getConnection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            conn.close()
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False

    def getHealthStatus(self):
        dbStatus = self.checkDatabase()

        status = {
            "service": "api-cinta-zakat",
            "status": "healthy" if dbStatus else "unhealthy",
            "database": "connected" if dbStatus else "disconnected"
        }

        statusCode = 200 if dbStatus else 503
        return Response.success(data=status, message="System Health Status", statusCode=statusCode)
