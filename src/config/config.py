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
    # Kredensial Sandbox (Hardcoded untuk stabilitas)
    DANA_CLIENT_ID = os.getenv("DANA_CLIENT_ID", "2026020413531650671653")          # Partner ID
    DANA_CLIENT_SECRET = os.getenv("DANA_CLIENT_SECRET", "1afcb6b638fbe9f4e399fde3cd195f2321d51f29d257c172c7b65458f5226d3d")  # Client Secret
    DANA_MERCHANT_ID = os.getenv("DANA_MERCHANT_ID", "216620010022044847375")      # Merchant ID
    
    # Environment: 'sandbox' (testing) atau 'production'
    DANA_ENV = os.getenv("DANA_ENV", "sandbox")

    # DANA Base URL - baca dari environment variable, atau gunakan default berdasarkan DANA_ENV
    # Sandbox: https://api.sandbox.dana.id (Sesuai dokumentasi terbaru)
    DANA_BASE_URL = os.getenv("DANA_BASE_URL", "https://api.sandbox.dana.id")

    # Security Keys (Gunakan path atau string kunci langsung)
    # Private Key Sandbox (Raw String)
    _DEFAULT_PRIVATE_KEY = "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDJ8CxxPqxg9dLE6R4z5A/5cZtE3hAn+NUKsv9YYNlvbYgwvbg0+RV5h+/n1wdVMXaAK6X4vdshTrWhOjnBPahyzfrwIPUHVVdWFi98T8zPRKiNH6xWYoXbOI25iq0zVXFbvhjeCO/vpG9cQM8tyuE0uJRKir7TO4WZmQm4m3NAp9lqq3RHpOTQgZE7K9HtGqq7bTZUMKIjf7Z2IPL1jyfcmNI3P2010jz8k6DbxZ/onYlDAww2h+p5NnlXemhMcu3dszyR48s/g18WMsh3HGIlw/BmZxxqoYgDPEFX4/00D6vBcuEDDR0MO4E0GP4cG791vzWlcaj+k/AHOeHf+lA7AgMBAAECggEAUTwo5LWNqsO5MjWFTOKl+nbVO3MJlMrpCRDQ38C2N7kcXF81xzmchfNFc0JxVLg9L3pfnhziFhgPwPgnW7FuHiD2nbrkVzrhk2QBXkTL42V/WKYxMd8YcgPiH43F9yycGYfzgP6fZwwDMF1x+r3ussK+BO6jrV34dL23x2fhiVREVyX7edeiTf4n+qaPHgrAchrlqN7ILE7r0j5egBBjNMBDo9/0cTR0qVyzdkVtX5i+AQlP5M/ZAMbGg7poGGH1qjErCyegu30QaRpAfnUNzQbBZONP0gh0QNqkRq41m/+K1qlPT1VEkK1eYtbqL/l3Yh8VHjWPvIfg5KJW8RIpoQKBgQDKR+VJta7rNM3HF4CsbZCvEovTIcolgqNe/SAk06AToB2oyC/MNTsfM6fI2HYkxOtopSSPhGDYPmIu3870fxMk/y9PhuxocNRirsj/9Cyt94xvR4SpfS4MzsuFXffgwa6kZjTFdjKB15aeV6ea6ILzY3ePJRAVknKKMOIeQp7vVQKBgQD/kPtaTqiGY/YSYB58ktMikeSdEm4W6bwkMQKByWM4YtJ45p36P08+HyJ8IB8qnMfwv1tGEKen1rMgsHIz4cjUSXScVBPlcAy/rLfgbjgZxJpok6IfIoFJUgw99raV62VZ8xHtKwIbv/x7O1GHLdAc3UbreGSMN21bTnI4BsKhTwKBgQCxSUgFTU4saVA9QTUOaszXFFsmRcQlEhVbqGBmxm/TI487IZD62mCh3SUd29HYMhrc0Xh0rKIwhKSKzq9VDJbb4yg0/FzwwIr0npod8oTCSGd2FGmKHuOgaBJqJkydWUNWZRm1Qv3LXQduagbEtyomZTQhamtpbLwkr+lOejdQLQKBgQDEb+Yjpe43TkJoIWWNjzWmjslQSkhAaGxqzRkGNYuEXcE1mN246ky4jSnuiqoqENRGIm+/zTFw+sA40icV5eh98/Aj8SRR6OyDr/iuE0of1FRzKXclw1nox54NSsNRPNxsZT9UMwit18Xz2sZxxy794L+QYru2Yyw1UHjOw7N6VQKBgQCczYC79QRCMMX0PwB0DkAzbdM1JTQGNym3z1xk+Pu/XhtJkJO8qymL4/phdHfa0ESehfIC0eNSf07vKrkIuY/vly7v+2CJ5athHXaIKVAF98RJ7kX2tgMFAekxYqHLoZVbQqV8uzV2S/e4txPVzl8OC0yC0G0KsozRbJVIoh7rKg=="
    
    DANA_PRIVATE_KEY = os.getenv("DANA_PRIVATE_KEY", _DEFAULT_PRIVATE_KEY)
    DANA_WEBHOOK_PUBLIC_KEY = os.getenv("DANA_WEBHOOK_PUBLIC_KEY", "")

    # Channel ID untuk API request
    DANA_CHANNEL_ID = os.getenv("DANA_CHANNEL_ID", "95221")

    # Origin domain
    # Origin domain used when communicating with DANA dashboard / whitelist
    DANA_ORIGIN = os.getenv("DANA_ORIGIN", "https://be-dana.vercel.app")

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