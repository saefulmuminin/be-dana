"""
DANA Mini Program Authentication Service
Untuk integrasi Seamless Login di DANA Mini App

Flow Mini Program:
1. Mini app call my.getAuthCode() -> dapat authCode dari DANA SDK
2. Mini app kirim authCode ke backend
3. Backend simpan session dan return JWT token
4. User sudah login

Catatan: Untuk Mini Program, exchange token dilakukan di DANA SDK side,
backend hanya perlu menerima dan menyimpan data user.
"""

from src.models.user_model import UserModel
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime
import json
import uuid
import jwt


class DanaAuthService:
    """
    DANA Mini Program Authentication Service
    """

    def __init__(self):
        self.userModel = UserModel()
        self.db = Database()
        self.jwtSecret = Config.JWT_SECRET
        self.jwtExpireHours = Config.JWT_EXPIRE_HOURS

    def logApiCall(self, endpoint, method, requestBody, responseStatus, responseBody, error=None):
        """Log API call ke database"""
        try:
            conn = self.db.getConnection()
            with conn.cursor() as cursor:
                safeRequest = self._maskSensitiveData(requestBody)
                sql = """
                    INSERT INTO log_api
                    (name, aplikasi, url_api, parameter, response, created_date, created_by, is_active, is_delete)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Y', 'N')
                """
                cursor.execute(sql, (
                    f"DANA_AUTH_{method}",
                    'DANA_MINIAPP',
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
        for key in ['auth_code', 'authCode', 'accessToken', 'refreshToken', 'token']:
            if key in masked and masked[key]:
                value = str(masked[key])
                masked[key] = value[:8] + '***' if len(value) > 8 else '***'
        return masked

    def applyToken(self, data):
        """
        Terima auth code dari Mini App dan buat session

        Untuk DANA Mini Program, auth code sudah di-exchange oleh SDK di mini app.
        Backend hanya perlu menerima dan membuat session.

        Args:
            data: {
                auth_code: Auth code dari my.getAuthCode()
                external_id: External ID untuk tracking
            }
        """
        try:
            authCode = data.get('auth_code')
            externalId = data.get('external_id') or str(uuid.uuid4())

            if not authCode:
                return Response.error("Auth code wajib diisi", 400)

            self.logApiCall('/apply-token', 'POST', data, 200, {'status': 'received'})

            # Untuk Mini Program, kita return success dengan external_id
            # Token akan di-generate di seamlessLogin
            return Response.success(data={
                "externalId": externalId,
                "authCode": authCode[:10] + "...",  # Partial for confirmation
                "message": "Auth code received, proceed to seamless login"
            }, message="Auth code berhasil diterima")

        except Exception as e:
            return Response.error(f"Apply token gagal: {str(e)}", 500)

    def seamlessLogin(self, data):
        """
        Seamless Login - Buat atau update user dan generate JWT

        Args:
            data: {
                external_id: External ID
                access_token: DANA access token (dari mini app)
                user_info: { name, phone, email } (optional, dari my.getOpenUserInfo)
            }
        """
        try:
            externalId = data.get('external_id') or str(uuid.uuid4())
            userInfo = data.get('user_info') or {}

            # Try to get or create user from database
            user = None
            dbUser = False
            try:
                user = self._getOrCreateUser(externalId, userInfo)
                dbUser = user is not None
            except Exception as dbError:
                print(f"Database user operation failed: {str(dbError)}")
                # Create mock user for testing without database
                user = {
                    'id': 0,
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': userInfo.get('email', f'{externalId}@dana.miniapp'),
                    'no_hp': userInfo.get('phone', ''),
                    'external_id': externalId
                }
                dbUser = False

            if not user:
                # Fallback to mock user
                user = {
                    'id': 0,
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': userInfo.get('email', f'{externalId}@dana.miniapp'),
                    'no_hp': userInfo.get('phone', ''),
                    'external_id': externalId
                }
                dbUser = False

            # Generate JWT token
            jwtToken = self._generateJwt(user)

            try:
                self.logApiCall('/seamless-login', 'POST',
                               {'external_id': externalId}, 200,
                               {'user_id': user.get('id')})
            except:
                pass  # Ignore logging errors

            return Response.success(data={
                "token": jwtToken,
                "user": {
                    "id": user.get('id'),
                    "name": user.get('nama') or user.get('nama_lengkap'),
                    "email": user.get('email'),
                    "phone": user.get('no_hp') or user.get('handphone'),
                    "external_id": externalId
                },
                "externalId": externalId,
                "dbUser": dbUser
            }, message="Login berhasil")

        except Exception as e:
            return Response.error(f"Seamless login gagal: {str(e)}", 500)

    def _getOrCreateUser(self, externalId, userInfo):
        """Get existing user atau create baru"""
        try:
            # Cari user berdasarkan external_id atau email
            email = userInfo.get('email')
            phone = userInfo.get('phone')

            user = None

            if email:
                user = self.userModel.findByEmail(email)

            if not user and phone:
                user = self.userModel.findByPhone(phone)

            if not user:
                # Create new user
                userData = {
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': email or f'{externalId}@dana.miniapp',
                    'no_hp': phone,
                    'external_id': externalId,
                    'created_date': datetime.now(),
                    'is_active': 'Y'
                }
                userId = self.userModel.create(userData)
                user = self.userModel.findById(userId)
            else:
                # Update external_id jika belum ada
                if not user.get('external_id'):
                    self.userModel.updateExternalId(user['id'], externalId)

            return user

        except Exception as e:
            print(f"Get/Create user error: {str(e)}")
            return None

    def _generateJwt(self, user):
        """Generate JWT token untuk user"""
        from datetime import timedelta

        payload = {
            'user_id': user.get('id'),
            'email': user.get('email'),
            'muzaki_id': user.get('muzaki_id'),
            'type': 'user',
            'exp': datetime.utcnow() + timedelta(hours=self.jwtExpireHours)
        }

        return jwt.encode(payload, self.jwtSecret, algorithm='HS256')

    def refreshToken(self, data):
        """Refresh expired token"""
        try:
            oldToken = data.get('token') or data.get('refresh_token')

            if not oldToken:
                return Response.error("Token wajib diisi", 400)

            try:
                # Decode without verification to get user_id
                payload = jwt.decode(oldToken, self.jwtSecret, algorithms=['HS256'],
                                    options={"verify_exp": False})
                userId = payload.get('user_id')

                user = self.userModel.findById(userId)
                if not user:
                    return Response.error("User tidak ditemukan", 404)

                # Generate new token
                newToken = self._generateJwt(user)

                return Response.success(data={
                    "token": newToken,
                    "expiresIn": self.jwtExpireHours * 3600
                }, message="Token berhasil di-refresh")

            except jwt.InvalidTokenError:
                return Response.error("Token tidak valid", 401)

        except Exception as e:
            return Response.error(f"Refresh token gagal: {str(e)}", 500)

    def generateOauthUrl(self, data):
        """
        Generate OAuth URL - Tidak diperlukan untuk Mini Program
        Mini Program menggunakan my.getAuthCode() langsung
        """
        return Response.success(data={
            "message": "Untuk DANA Mini Program, gunakan my.getAuthCode() di mini app",
            "note": "Backend tidak perlu generate OAuth URL"
        }, message="Mini Program tidak memerlukan OAuth URL")

    def getUserInfo(self, accessToken):
        """Get user info - placeholder untuk compatibility"""
        return Response.success(data={}, message="Use my.getOpenUserInfo() in mini app")
