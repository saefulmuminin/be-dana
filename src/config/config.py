import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ==========================================================================
    # DATABASE CONFIGURATION (PostgreSQL - Neon)
    # ==========================================================================
    # Gunakan DATABASE_URL untuk PostgreSQL (Neon/Vercel Postgres)
    DATABASE_URL = os.getenv('DATABASE_URL', '')

    # Fix untuk SQLAlchemy - ganti postgres:// dengan postgresql://
    @staticmethod
    def get_database_url():
        uri = os.getenv('DATABASE_URL', '')
        if uri and uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri

    # Legacy MySQL config (deprecated, gunakan DATABASE_URL)
    DB_HOST = os.getenv('DB_HOST', '')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_NAME = os.getenv('DB_NAME', '')

    # ==========================================================================
    # APPLICATION CONFIGURATION
    # ==========================================================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-change-in-production')
    JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '24'))

    # App URLs
    APP_URL = os.getenv('APP_URL', 'https://cintazakat.id')
    APP_REDIRECT_URL = os.getenv('APP_REDIRECT_URL', 'https://app.cintazakat.id')
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.cintazakat.id')

    # ==========================================================================
    # SIMBA INTEGRATION
    # ==========================================================================
    SIMBA_URL = os.getenv("SIMBA_URL", "https://demo-simba.baznas.or.id/")
    SIMBA_KEY = os.getenv("SIMBA_KEY", "")
    SIMBA_ORG = os.getenv("SIMBA_ORG", "")
    API_MUZAKI_REGISTER = os.getenv("API_MUZAKI_REGISTER", "api/ajax_muzaki_register")
    API_MUZAKI_EDIT = os.getenv("API_MUZAKI_EDIT", "api2/muzaki_edit")

    # ==========================================================================
    # DANA WIDGET BINDING CONFIGURATION
    # Dokumentasi: https://dashboard.dana.id/api-docs
    # Library: pip install dana-python
    # ==========================================================================

    # Required Credentials (dari merchant portal DANA)
    DANA_CLIENT_ID = os.getenv("DANA_CLIENT_ID", "")          # X_PARTNER_ID
    DANA_CLIENT_SECRET = os.getenv("DANA_CLIENT_SECRET", "")  # Client Secret
    DANA_MERCHANT_ID = os.getenv("DANA_MERCHANT_ID", "")      # Merchant ID
    DANA_CHANNEL_ID = os.getenv("DANA_CHANNEL_ID", "")        # Channel ID

    # Private Key untuk API Authentication
    # Bisa set langsung atau path ke file
    DANA_PRIVATE_KEY = os.getenv("DANA_PRIVATE_KEY", "")
    DANA_PRIVATE_KEY_PATH = os.getenv("DANA_PRIVATE_KEY_PATH", "")

    # Environment: 'sandbox' atau 'production'
    DANA_ENV = os.getenv("DANA_ENV", "sandbox")

    # Base URL sesuai environment
    DANA_BASE_URL = os.getenv("DANA_BASE_URL",
        "https://api-sandbox.dana.id" if os.getenv("DANA_ENV", "sandbox") == "sandbox"
        else "https://api.dana.id"
    )

    # Origin URL (URL aplikasi Anda)
    DANA_ORIGIN = os.getenv("DANA_ORIGIN", APP_URL)

    # Webhook Configuration
    DANA_WEBHOOK_PUBLIC_KEY = os.getenv("DANA_WEBHOOK_PUBLIC_KEY", "")
    DANA_WEBHOOK_PUBLIC_KEY_PATH = os.getenv("DANA_WEBHOOK_PUBLIC_KEY_PATH", "")

    # Callback URLs
    DANA_REDIRECT_URL = os.getenv("DANA_REDIRECT_URL", f"{API_BASE_URL}/api/v1/auth/finish-redirect")
    DANA_FINISH_PAYMENT_URL = os.getenv("DANA_FINISH_PAYMENT_URL", f"{API_BASE_URL}/api/v1/dana/finish-payment")
    DANA_WEBHOOK_URL = os.getenv("DANA_WEBHOOK_URL", f"{API_BASE_URL}/api/v1/dana/webhook")
