"""
DANA OAuth Authentication Service
Menggunakan library resmi dana-python untuk Widget Binding (Seamless Login)

Flow DANA Widget Binding:
1. Generate OAuth URL -> User redirect ke DANA
2. User login di DANA -> Redirect back dengan auth_code
3. Apply Token (exchange auth_code -> access_token)
4. Gunakan access_token untuk transaksi

Dokumentasi: https://dashboard.dana.id/api-docs
Library: pip install dana-python
"""

from src.models.user_model import UserModel
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime
import json
import uuid
import urllib.parse

# Import DANA official library
try:
    from dana.ipg import v1 as dana_ipg
    DANA_SDK_AVAILABLE = True
except ImportError:
    DANA_SDK_AVAILABLE = False
    print("WARNING: dana-python library not installed. Run: pip install dana-python")


class DanaAuthService:
    """
    DANA OAuth Authentication Service untuk Widget Binding
    """

    def __init__(self):
        self.userModel = UserModel()
        self.db = Database()

        # DANA Credentials
        self.partnerId = Config.DANA_CLIENT_ID  # X_PARTNER_ID
        self.merchantId = Config.DANA_MERCHANT_ID
        self.channelId = getattr(Config, 'DANA_CHANNEL_ID', 'channel_id')
        self.clientSecret = Config.DANA_CLIENT_SECRET
        self.privateKey = getattr(Config, 'DANA_PRIVATE_KEY', None)
        self.privateKeyPath = getattr(Config, 'DANA_PRIVATE_KEY_PATH', None)
        self.origin = getattr(Config, 'DANA_ORIGIN', 'https://cintazakat.id')
        self.env = getattr(Config, 'DANA_ENV', 'sandbox')

        # URLs
        self.baseUrl = Config.DANA_BASE_URL
        self.oauthUrl = f"{self.baseUrl}/v1.0/get-auth-url"
        self.tokenUrl = f"{self.baseUrl}/v1.0/access-token/b2b2c"

    def _initDanaClient(self):
        """Initialize DANA SDK environment"""
        if not DANA_SDK_AVAILABLE:
            return False

        import os
        os.environ['X_PARTNER_ID'] = self.partnerId
        os.environ['MERCHANT_ID'] = self.merchantId
        os.environ['CHANNEL_ID'] = self.channelId
        os.environ['ORIGIN'] = self.origin
        os.environ['ENV'] = self.env

        if self.privateKey:
            os.environ['PRIVATE_KEY'] = self.privateKey
        elif self.privateKeyPath:
            os.environ['PRIVATE_KEY_PATH'] = self.privateKeyPath

        return True

    def logApiCall(self, endpoint, method, requestBody, responseStatus, responseBody, error=None):
        """Log API call ke database"""
        try:
            conn = self.db.getConnection()
            with conn.cursor() as cursor:
                # Mask sensitive data
                safeRequest = self._maskSensitiveData(requestBody)

                sql = """
                    INSERT INTO log_api
                    (name, aplikasi, url_api, parameter, response, created_date, created_by, is_active, is_delete)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y', 'N')
                """
                cursor.execute(sql, (
                    f"DANA_AUTH_{method}",
                    'DANA_WIDGET',
                    endpoint,
                    json.dumps(safeRequest) if safeRequest else None,
                    json.dumps(responseBody) if responseBody else str(error),
                    datetime.now(),
                    'system'
                ))
                conn.commit()
        except Exception as e:
            print(f"Failed to log: {str(e)}")

    def _maskSensitiveData(self, data):
        """Mask sensitive data untuk logging"""
        if not data or not isinstance(data, dict):
            return data

        masked = data.copy()
        for key in ['code', 'authCode', 'accessToken', 'refreshToken', 'privateKey']:
            if key in masked and masked[key]:
                value = str(masked[key])
                masked[key] = value[:8] + '***' if len(value) > 8 else '***'
        return masked

    def generateOauthUrl(self, data):
        """
        Generate OAuth URL untuk DANA Widget Binding

        User akan di-redirect ke URL ini untuk login/authorize di DANA

        Args:
            data: {
                redirect_url: URL callback setelah user selesai di DANA
                mobile_number: Nomor HP user untuk seamless (optional)
                external_id: Tracking ID (optional)
                scopes: OAuth scopes (optional)
            }

        Returns:
            {
                oauthUrl: URL untuk redirect user
                externalId: ID untuk tracking
            }
        """
        try:
            externalId = data.get('external_id') or str(uuid.uuid4())
            redirectUrl = data.get('redirect_url')
            mobileNumber = data.get('mobile_number')

            if not redirectUrl:
                return Response.error("Redirect URL wajib diisi", 400)

            if DANA_SDK_AVAILABLE:
                return self._generateOauthUrlWithSDK(externalId, redirectUrl, mobileNumber)
            else:
                return self._generateOauthUrlFallback(externalId, redirectUrl, mobileNumber)

        except Exception as e:
            return Response.error(f"Gagal generate OAuth URL: {str(e)}", 500)

    def _generateOauthUrlWithSDK(self, externalId, redirectUrl, mobileNumber=None):
        """Generate OAuth URL menggunakan DANA SDK"""
        try:
            self._initDanaClient()

            request_data = {
                "merchantId": self.merchantId,
                "externalId": externalId,
                "redirectUrl": redirectUrl,
                "scopes": "QUERY_BALANCE,CASHOUT,MINI_DANA"
            }

            if mobileNumber:
                request_data["seamlessData"] = {
                    "mobileNumber": mobileNumber
                }

            response = dana_ipg.get_auth_url(request_data)

            self.logApiCall('dana_ipg.get_auth_url', 'POST', request_data, 200, response)

            if response.get('responseCode') in ['2007300', '00']:
                return Response.success(data={
                    "oauthUrl": response.get('webRedirectUrl'),
                    "externalId": externalId
                }, message="OAuth URL berhasil digenerate")
            else:
                return Response.error(
                    f"DANA Error: {response.get('responseMessage')}",
                    400
                )

        except Exception as e:
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _generateOauthUrlFallback(self, externalId, redirectUrl, mobileNumber=None):
        """Generate OAuth URL tanpa SDK (manual build URL)"""
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

        requestBody = {
            "merchantId": self.merchantId,
            "externalId": externalId,
            "redirectUrl": redirectUrl,
            "scopes": "QUERY_BALANCE,CASHOUT,MINI_DANA"
        }

        if mobileNumber:
            requestBody["seamlessData"] = {"mobileNumber": mobileNumber}

        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/get-auth-url"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "CHANNEL-ID": self.channelId,
            "X-EXTERNAL-ID": externalId
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            self.logApiCall(url, 'POST', requestBody, response.status_code, result)

            if response.status_code == 200 and result.get('webRedirectUrl'):
                return Response.success(data={
                    "oauthUrl": result.get('webRedirectUrl'),
                    "externalId": externalId
                }, message="OAuth URL berhasil digenerate")
            else:
                # Return full DANA response for debugging
                error_msg = result.get('responseMessage') or result.get('message') or json.dumps(result)
                return Response.error(f"DANA Error [{response.status_code}]: {error_msg}", 400)

        except Exception as e:
            return Response.error(f"Request failed: {str(e)}", 500)

    def applyToken(self, data):
        """
        Exchange authorization code untuk access token

        Dipanggil setelah user selesai authorize di DANA dan redirect back

        Args:
            data: {
                auth_code: Authorization code dari DANA callback
                external_id: External ID dari step sebelumnya
            }

        Returns:
            {
                accessToken: Token untuk transaksi
                refreshToken: Token untuk refresh
                expiresIn: Masa berlaku dalam detik
            }
        """
        try:
            authCode = data.get('auth_code')
            externalId = data.get('external_id')

            if not authCode:
                return Response.error("Authorization code wajib diisi", 400)
            if not externalId:
                return Response.error("External ID wajib diisi", 400)

            if DANA_SDK_AVAILABLE:
                return self._applyTokenWithSDK(authCode, externalId)
            else:
                return self._applyTokenFallback(authCode, externalId)

        except Exception as e:
            return Response.error(f"Apply token gagal: {str(e)}", 500)

    def _applyTokenWithSDK(self, authCode, externalId):
        """Apply token menggunakan DANA SDK"""
        try:
            self._initDanaClient()

            request_data = {
                "grantType": "AUTHORIZATION_CODE",
                "authCode": authCode,
                "merchantId": self.merchantId
            }

            response = dana_ipg.apply_token(request_data)

            # Log dengan masked data
            self.logApiCall('dana_ipg.apply_token', 'POST',
                           {'grantType': 'AUTHORIZATION_CODE', 'authCode': authCode[:8] + '***'},
                           200, self._maskSensitiveData(response))

            if response.get('responseCode') in ['2007400', '00']:
                return Response.success(data={
                    "accessToken": response.get('accessToken'),
                    "refreshToken": response.get('refreshToken'),
                    "expiresIn": response.get('accessTokenExpiryTime', 94608000),
                    "tokenType": "Bearer",
                    "externalId": externalId
                }, message="Token berhasil didapatkan")
            else:
                return Response.error(
                    f"DANA Error: {response.get('responseMessage')}",
                    400
                )

        except Exception as e:
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _applyTokenFallback(self, authCode, externalId):
        """Apply token tanpa SDK"""
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

        requestBody = {
            "grantType": "AUTHORIZATION_CODE",
            "authCode": authCode,
            "merchantId": self.merchantId
        }

        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/access-token/b2b2c"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "CHANNEL-ID": self.channelId,
            "X-EXTERNAL-ID": externalId
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            self.logApiCall(url, 'POST',
                           {'grantType': 'AUTHORIZATION_CODE'},
                           response.status_code,
                           self._maskSensitiveData(result))

            if response.status_code == 200:
                return Response.success(data={
                    "accessToken": result.get('accessToken'),
                    "refreshToken": result.get('refreshToken'),
                    "expiresIn": result.get('accessTokenExpiryTime', 94608000),
                    "tokenType": "Bearer",
                    "externalId": externalId
                }, message="Token berhasil didapatkan")
            else:
                return Response.error(f"DANA Error: {result.get('responseMessage')}", 400)

        except Exception as e:
            return Response.error(f"Request failed: {str(e)}", 500)

    def refreshToken(self, data):
        """
        Refresh expired access token

        Args:
            data: {
                refresh_token: Refresh token dari sebelumnya
            }
        """
        try:
            refreshTokenValue = data.get('refresh_token')

            if not refreshTokenValue:
                return Response.error("Refresh token wajib diisi", 400)

            if DANA_SDK_AVAILABLE:
                return self._refreshTokenWithSDK(refreshTokenValue)
            else:
                return self._refreshTokenFallback(refreshTokenValue)

        except Exception as e:
            return Response.error(f"Refresh token gagal: {str(e)}", 500)

    def _refreshTokenWithSDK(self, refreshTokenValue):
        """Refresh token menggunakan SDK"""
        try:
            self._initDanaClient()

            request_data = {
                "grantType": "REFRESH_TOKEN",
                "refreshToken": refreshTokenValue,
                "merchantId": self.merchantId
            }

            response = dana_ipg.apply_token(request_data)

            if response.get('responseCode') in ['2007400', '00']:
                return Response.success(data={
                    "accessToken": response.get('accessToken'),
                    "refreshToken": response.get('refreshToken'),
                    "expiresIn": response.get('accessTokenExpiryTime', 94608000),
                    "tokenType": "Bearer"
                }, message="Token berhasil di-refresh")
            else:
                return Response.error(f"DANA Error: {response.get('responseMessage')}", 400)

        except Exception as e:
            return Response.error(f"DANA SDK Error: {str(e)}", 500)

    def _refreshTokenFallback(self, refreshTokenValue):
        """Refresh token tanpa SDK"""
        import requests
        import hmac
        from hashlib import sha256

        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        externalId = str(uuid.uuid4())

        requestBody = {
            "grantType": "REFRESH_TOKEN",
            "refreshToken": refreshTokenValue,
            "merchantId": self.merchantId
        }

        bodyStr = json.dumps(requestBody, separators=(',', ':'), sort_keys=True)
        path = "/v1.0/access-token/b2b2c"
        stringToSign = f"{timestamp}POST{path}{bodyStr}"
        signature = hmac.new(
            self.clientSecret.encode(),
            stringToSign.encode(),
            sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-PARTNER-ID": self.partnerId,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "CHANNEL-ID": self.channelId,
            "X-EXTERNAL-ID": externalId
        }

        url = f"{self.baseUrl}{path}"

        try:
            response = requests.post(url, json=requestBody, headers=headers, timeout=30)
            result = response.json() if response.text else {}

            if response.status_code == 200:
                return Response.success(data={
                    "accessToken": result.get('accessToken'),
                    "refreshToken": result.get('refreshToken'),
                    "expiresIn": result.get('accessTokenExpiryTime', 94608000),
                    "tokenType": "Bearer"
                }, message="Token berhasil di-refresh")
            else:
                return Response.error(f"DANA Error: {result.get('responseMessage')}", 400)

        except Exception as e:
            return Response.error(f"Request failed: {str(e)}", 500)

    def getUserInfo(self, accessToken):
        """
        Get user info dari DANA (balance, profile, dll)
        """
        # TODO: Implement if needed
        return Response.success(data={}, message="Not implemented")
