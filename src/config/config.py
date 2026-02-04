import os
from dotenv import load_dotenv

# Memuat file .env jika dijalankan secara lokal
load_dotenv()

class Config:
    # ==========================================================================
    # DATABASE CONFIGURATION (Auto-detect Vercel/Neon/Local)
    # ==========================================================================
    # Vercel menyediakan POSTGRES_URL secara otomatis saat kita klik "Connect"
    # Kita juga mengecek STORAGE_URL (jika Anda pakai prefix) atau DATABASE_URL
    SQLALCHEMY_DATABASE_URI = (
        os.getenv('POSTGRES_URL') or 
        os.getenv('STORAGE_URL') or 
        os.getenv('DATABASE_URL') or
        "sqlite:///local_test.db"  # Fallback ke SQLite jika tidak ada DB sama sekali
    )

    # Fix untuk SQLAlchemy: Dialek 'postgres://' sudah deprecated, harus 'postgresql://'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    # Mematikan fitur tracking untuk menghemat memori di serverless (Vercel)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================================================
    # APPLICATION CONFIGURATION
    # ==========================================================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-12345')
    JWT_SECRET = os.getenv('JWT_SECRET', 'default-jwt-secret-67890')
    JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', '24'))

    # Base URLs - Gunakan URL Vercel Anda di Environment Variables (APP_URL)
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    API_BASE_URL = os.getenv('API_BASE_URL', APP_URL)

    # ==========================================================================
    # DANA WIDGET BINDING CONFIGURATION
    # ==========================================================================
    # Kredensial ini diambil dari Dashboard DANA (Screenshot yang Anda kirim)
    DANA_CLIENT_ID = os.getenv("DANA_CLIENT_ID", "")          # Partner ID
    DANA_CLIENT_SECRET = os.getenv("DANA_CLIENT_SECRET", "")  # Client Secret
    DANA_MERCHANT_ID = os.getenv("DANA_MERCHANT_ID", "")      # Merchant ID
    
    # Environment: 'sandbox' (testing) atau 'production'
    DANA_ENV = os.getenv("DANA_ENV", "sandbox")
    DANA_BASE_URL = (
        "https://api-sandbox.dana.id" if DANA_ENV == "sandbox" 
        else "https://api-sandbox.dana.id"
    )

    # Security Keys (Gunakan path atau string kunci langsung)
    DANA_PRIVATE_KEY = os.getenv("DANA_PRIVATE_KEY", "")
    DANA_WEBHOOK_PUBLIC_KEY = os.getenv("DANA_WEBHOOK_PUBLIC_KEY", "")

    # ==========================================================================
    # CALLBACK URLS (Input ini ke Dashboard DANA)
    # ==========================================================================
    # URL ini yang harus dimasukkan ke gambar "Finish Payment URL" dsb.
    DANA_FINISH_PAYMENT_URL = f"{API_BASE_URL}/api/v1/dana/finish-payment"
    DANA_WEBHOOK_URL = f"{API_BASE_URL}/api/v1/dana/webhook"
    DANA_REDIRECT_URL = f"{API_BASE_URL}/api/v1/auth/finish-redirect"

    # ==========================================================================
    # SIMBA INTEGRATION (BAZNAS)
    # ==========================================================================
    SIMBA_URL = os.getenv("SIMBA_URL", "https://demo-simba.baznas.or.id/")
    SIMBA_KEY = os.getenv("SIMBA_KEY", "")
    SIMBA_ORG = os.getenv("SIMBA_ORG", "")