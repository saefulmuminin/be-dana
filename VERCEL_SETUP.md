# Vercel Environment Variables Setup

## ⚠️ CRITICAL: Set These Environment Variables

Go to: https://vercel.com/your-project/settings/environment-variables

### Required Variables

```bash
# Database
POSTGRES_URL=your_postgres_connection_string

# DANA Credentials
DANA_CLIENT_ID=2026020413531650671653
DANA_CLIENT_SECRET=1afcb6b638fbe9f4e399fde3cd195f2321d51f29d257c172c7b65458f5226d3d
DANA_MERCHANT_ID=216620010022044847375
DANA_CHANNEL_ID=95221

# DANA Environment
DANA_ENV=sandbox
DANA_BASE_URL=https://api.sandbox.dana.id
DANA_ORIGIN=https://cintazakat.id

# DANA Private Key (IMPORTANT: Copy exactly as one line, no line breaks)
DANA_PRIVATE_KEY=MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDJ8CxxPqxg9dLE6R4z5A/5cZtE3hAn+NUKsv9YYNlvbYgwvbg0+RV5h+/n1wdVMXaAK6X4vdshTrWhOjnBPahyzfrwIPUHVVdWFi98T8zPRKiNH6xWYoXbOI25iq0zVXFbvhjeCO/vpG9cQM8tyuE0uJRKir7TO4WZmQm4m3NAp9lqq3RHpOTQgZE7K9HtGqq7bTZUMKIjf7Z2IPL1jyfcmNI3P2010jz8k6DbxZ/onYlDAww2h+p5NnlXemhMcu3dszyR48s/g18WMsh3HGIlw/BmZxxqoYgDPEFX4/00D6vBcuEDDR0MO4E0GP4cG791vzWlcaj+k/AHOeHf+lA7AgMBAAECggEAUTwo5LWNqsO5MjWFTOKl+nbVO3MJlMrpCRDQ38C2N7kcXF81xzmchfNFc0JxVLg9L3pfnhziFhgPwPgnW7FuHiD2nbrkVzrhk2QBXkTL42V/WKYxMd8YcgPiH43F9yycGYfzgP6fZwwDMF1x+r3ussK+BO6jrV34dL23x2fhiVREVyX7edeiTf4n+qaPHgrAchrlqN7ILE7r0j5egBBjNMBDo9/0cTR0qVyzdkVtX5i+AQlP5M/ZAMbGg7poGGH1qjErCyegu30QaRpAfnUNzQbBZONP0gh0QNqkRq41m/+K1qlPT1VEkK1eYtbqL/l3Yh8VHjWPvIfg5KJW8RIpoQKBgQDKR+VJta7rNM3HF4CsbZCvEovTIcolgqNe/SAk06AToB2oyC/MNTsfM6fI2HYkxOtopSSPhGDYPmIu3870fxMk/y9PhuxocNRirsj/9Cyt94xvR4SpfS4MzsuFXffgwa6kZjTFdjKB15aeV6ea6ILzY3ePJRAVknKKMOIeQp7vVQKBgQD/kPtaTqiGY/YSYB58ktMikeSdEm4W6bwkMQKByWM4YtJ45p36P08+HyJ8IB8qnMfwv1tGEKen1rMgsHIz4cjUSXScVBPlcAy/rLfgbjgZxJpok6IfIoFJUgw99raV62VZ8xHtKwIbv/x7O1GHLdAc3UbreGSMN21bTnI4BsKhTwKBgQCxSUgFTU4saVA9QTUOaszXFFsmRcQlEhVbqGBmxm/TI487IZD62mCh3SUd29HYMhrc0Xh0rKIwhKSKzq9VDJbb4yg0/FzwwIr0npod8oTCSGd2FGmKHuOgaBJqJkydWUNWZRm1Qv3LXQduagbEtyomZTQhamtpbLwkr+lOejdQLQKBgQDEb+Yjpe43TkJoIWWNjzWmjslQSkhAaGxqzRkGNYuEXcE1mN246ky4jSnuiqoqENRGIm+/zTFw+sA40icV5eh98/Aj8SRR6OyDr/iuE0of1FRzKXclw1nox54NSsNRPNxsZT9UMwit18Xz2sZxxy794L+QYru2Yyw1UHjOw7N6VQKBgQCczYC79QRCMMX0PwB0DkAzbdM1JTQGNym3z1xk+Pu/XhtJkJO8qymL4/phdHfa0ESehfIC0eNSf07vKrkIuY/vly7v+2CJ5athHXaIKVAF98RJ7kX2tgMFAekxYqHLoZVbQqV8uzV2S/e4txPVzl8OC0yC0G0KsozRbJVIoh7rKg==

# Development Mode (SET THIS FOR TESTING)
DANA_DEV_MODE=true

# Security
SECRET_KEY=apicintazakat
JWT_SECRET=your_jwt_secret_key_change_in_production
JWT_EXPIRE_HOURS=24

# Application URLs
APP_URL=https://be-dana.vercel.app
API_BASE_URL=https://be-dana.vercel.app

# SIMBA (Optional)
SIMBA_URL=https://demo-simba.baznas.or.id/
SIMBA_KEY=your_simba_key
SIMBA_ORG=9977200
```

## 🚨 IMPORTANT

1. **DANA_DEV_MODE=true** → This allows testing without waiting for DANA API fix
2. **DANA_CHANNEL_ID=95221** → Must be exactly "95221", not "your_channel_id"
3. **DANA_PRIVATE_KEY** → Must be one continuous line, no line breaks

## After Setting Variables

1. Go to Deployments tab
2. Click "..." on latest deployment
3. Click "Redeploy"
4. Wait 1-2 minutes
5. Test: `curl https://be-dana.vercel.app/api/v1/dana/create-order -X POST -H "Content-Type: application/json" -d '{"nominal":10000,"email":"test@test.com","nama_lengkap":"Test"}'`

## Expected Response with Dev Mode

```json
{
  "status": "success",
  "data": {
    "orderId": "DANA-20260206...",
    "tradeNO": "DANA-20260206...",
    "danaApiCalled": false,
    "amount": 10000
  }
}
```
