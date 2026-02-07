"""
DANA Mini Program Authentication Service

Flow:
1. Mini app call my.getAuthCode({ scopes: ['USER_LOGIN_ID', 'USER_CONTACTINFO_EMAIL'] })
2. Mini app kirim authCode ke backend
3. Backend exchange authCode ke DANA API -> dapat accessToken
4. Backend query user info ke DANA API -> dapat phone/email asli dari akun DANA
5. Backend create/find user di database berdasarkan email -> generate JWT
6. Return JWT token ke mini app

API Reference:
- Apply Token (B2B2C): POST /v1.0/access-token/b2b2c
"""

from src.models.user_model import UserModel
from src.utils.response import Response
from src.utils.database import Database
from src.config.config import Config
from datetime import datetime, timezone, timedelta
import json
import uuid
import jwt
import requests
import hashlib
import base64

# RSA Signature imports
try:
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    CRYPTO_AVAILABLE = True
except ImportError:
    try:
        from Cryptodome.Signature import PKCS1_v1_5
        from Cryptodome.Hash import SHA256
        from Cryptodome.PublicKey import RSA
        CRYPTO_AVAILABLE = True
    except ImportError:
        CRYPTO_AVAILABLE = False
        print("Warning: PyCryptodome not installed.")


class DanaAuthService:

    def __init__(self):
        self.userModel = UserModel()
        self.db = Database()
        self.jwtSecret = Config.JWT_SECRET
        self.jwtExpireHours = Config.JWT_EXPIRE_HOURS

    # =========================================================================
    # DANA API - Signature & Token Exchange
    # =========================================================================

    def _generateSignature(self, httpMethod, endpointUrl, requestBody, timestamp):
        """Generate RSA signature (PKCS1_v1_5 + SHA256) untuk DANA SNAP API"""
        try:
            if not CRYPTO_AVAILABLE:
                return None

            privateKey = Config.DANA_PRIVATE_KEY
            if not privateKey:
                return None

            if '\\n' in privateKey:
                privateKey = privateKey.replace('\\n', '\n')

            if not privateKey.startswith('-----BEGIN'):
                keyBody = privateKey.strip()
                lines = [keyBody[i:i+64] for i in range(0, len(keyBody), 64)]
                formattedKey = '\n'.join(lines)
                privateKey = f"-----BEGIN RSA PRIVATE KEY-----\n{formattedKey}\n-----END RSA PRIVATE KEY-----"

            bodyStr = json.dumps(requestBody, separators=(',', ':')) if requestBody else ''
            bodyHash = hashlib.sha256(bodyStr.encode('utf-8')).hexdigest().lower()
            stringToSign = f"{httpMethod}:{endpointUrl}:{bodyHash}:{timestamp}"

            pkey = RSA.importKey(privateKey)
            signer = PKCS1_v1_5.new(pkey)
            digest = SHA256.new()
            digest.update(stringToSign.encode('utf-8'))
            return base64.b64encode(signer.sign(digest)).decode('utf-8')

        except Exception as e:
            print(f"[AUTH] Signature failed: {str(e)}")
            return None

    def _exchangeAuthCode(self, authCode):
        """
        Exchange authCode dari my.getAuthCode() → accessToken via DANA API
        POST /v1.0/access-token/b2b2c
        """
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/access-token/b2b2c"
            fullUrl = f"{baseUrl}{endpoint}"

            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')

            requestBody = {
                "grantType": "AUTHORIZATION_CODE",
                "authCode": authCode
            }

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)
            if not signature:
                return {'success': False, 'error': 'Signature generation failed'}

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-CLIENT-KEY': Config.DANA_CLIENT_ID,
                'X-SIGNATURE': signature
            }

            print(f"[AUTH] Exchange authCode → {fullUrl}")
            print(f"[AUTH] authCode: {authCode[:15]}...")

            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            print(f"[AUTH] DANA token response: {response.status_code} → {response.text[:300]}")

            self.logApiCall(endpoint, 'POST', {'authCode': authCode[:10] + '***'},
                           response.status_code, response.text[:500])

            if response.ok:
                respData = response.json()
                responseCode = respData.get('responseCode', '')

                if responseCode == '2007300' or respData.get('accessToken'):
                    print(f"[AUTH] Got accessToken!")
                    return {
                        'success': True,
                        'accessToken': respData.get('accessToken'),
                        'refreshToken': respData.get('refreshToken'),
                        'expiresIn': respData.get('expiresIn', 900)
                    }
                else:
                    return {'success': False, 'error': f"{responseCode}: {respData.get('responseMessage', '')}"}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"[AUTH] Exchange failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _queryUserInfo(self, accessToken):
        """
        Query user info dari DANA menggunakan accessToken
        Endpoint bisa: /v1.0/user/profile/query atau /v1.0/registration/account/inquiry
        """
        try:
            baseUrl = Config.DANA_BASE_URL
            endpoint = "/v1.0/registration/account/inquiry"
            fullUrl = f"{baseUrl}{endpoint}"

            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')

            requestBody = {}

            signature = self._generateSignature("POST", endpoint, requestBody, timestamp)

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-PARTNER-ID': Config.DANA_CLIENT_ID,
                'X-EXTERNAL-ID': f"UQ-{uuid.uuid4().hex[:12].upper()}",
                'CHANNEL-ID': Config.DANA_CHANNEL_ID,
                'X-SIGNATURE': signature,
                'Authorization': f"Bearer {accessToken}"
            }

            print(f"[AUTH] Query user info → {fullUrl}")

            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            print(f"[AUTH] User info response: {response.status_code} → {response.text[:300]}")

            self.logApiCall(endpoint, 'POST', {'token': '***'},
                           response.status_code, response.text[:500])

            if response.ok:
                respData = response.json()
                # DANA bisa return di berbagai field tergantung API version
                userInfo = respData.get('userInfo') or respData.get('additionalInfo') or respData
                return {
                    'success': True,
                    'phone': userInfo.get('loginId') or userInfo.get('phone') or userInfo.get('mobile', ''),
                    'email': userInfo.get('email', ''),
                    'name': userInfo.get('name') or userInfo.get('nickName') or userInfo.get('fullName', ''),
                    'raw': respData
                }
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"[AUTH] Query user info failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Main Auth Endpoints
    # =========================================================================

    def applyToken(self, data):
        """Terima auth code dari Mini App"""
        try:
            authCode = data.get('auth_code')
            externalId = data.get('external_id') or str(uuid.uuid4())

            if not authCode:
                return Response.error("Auth code wajib diisi", 400)

            self.logApiCall('/apply-token', 'POST', data, 200, {'status': 'received'})

            return Response.success(data={
                "externalId": externalId,
                "authCode": authCode[:10] + "...",
                "message": "Auth code received"
            }, message="Auth code berhasil diterima")

        except Exception as e:
            return Response.error(f"Apply token gagal: {str(e)}", 500)

    def seamlessLogin(self, data):
        """
        Seamless Login - Exchange authCode, get real user info, generate JWT

        Flow:
        1. Terima authCode dari frontend (dari my.getAuthCode)
        2. Exchange authCode ke DANA API → accessToken
        3. Query user info dari DANA API → real phone/email
        4. Create/find user di database (match by email)
        5. Return JWT token
        """
        try:
            externalId = data.get('external_id') or str(uuid.uuid4())
            authCode = data.get('auth_code')
            frontendUserInfo = data.get('user_info') or {}

            print(f"[AUTH] === Seamless Login ===")
            print(f"[AUTH] externalId: {externalId}")
            print(f"[AUTH] hasAuthCode: {bool(authCode)}")
            print(f"[AUTH] frontendUserInfo: {json.dumps(frontendUserInfo)}")

            if not authCode:
                return Response.error("auth_code wajib diisi. Gunakan my.getAuthCode() di mini app.", 400)

            # =============================================================
            # Step 1-2: Exchange authCode & Get real user info dari DANA
            # =============================================================
            danaUserInfo = {}
            danaAccessToken = None
            exchangeError = None

            print(f"[AUTH] Exchanging authCode with DANA API...")

            # Exchange authCode → accessToken
            tokenResult = self._exchangeAuthCode(authCode)

            if tokenResult.get('success'):
                danaAccessToken = tokenResult.get('accessToken')
                print(f"[AUTH] accessToken obtained: {danaAccessToken[:20]}...")

                # Query real user info dari DANA
                userResult = self._queryUserInfo(danaAccessToken)

                if userResult.get('success'):
                    danaUserInfo = {
                        'phone': userResult.get('phone', ''),
                        'email': userResult.get('email', ''),
                        'name': userResult.get('name', '')
                    }
                    print(f"[AUTH] DANA user: phone={danaUserInfo['phone']}, email={danaUserInfo['email']}")
                else:
                    exchangeError = f"User query failed: {userResult.get('error')}"
                    print(f"[AUTH] {exchangeError} - using frontend info as fallback")
            else:
                exchangeError = f"Token exchange failed: {tokenResult.get('error')}"
                print(f"[AUTH] {exchangeError} - using frontend info as fallback")

            # =============================================================
            # Step 3: Merge user info (DANA API data > frontend data)
            # =============================================================
            userInfo = {
                'name': danaUserInfo.get('name') or frontendUserInfo.get('name', ''),
                'phone': danaUserInfo.get('phone') or frontendUserInfo.get('phone', ''),
                'email': danaUserInfo.get('email') or frontendUserInfo.get('email', '')
            }
            print(f"[AUTH] Final user info: {json.dumps(userInfo)}")

            # =============================================================
            # Step 4: Get or create user in database
            # =============================================================
            user = None
            dbUser = False
            try:
                user = self._getOrCreateUser(externalId, userInfo)
                dbUser = user is not None
            except Exception as dbError:
                print(f"[AUTH] DB error: {str(dbError)}")
                user = {
                    'id': 0,
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': userInfo.get('email', f'{externalId}@dana.miniapp'),
                    'no_hp': userInfo.get('phone', ''),
                    'external_id': externalId
                }

            if not user:
                user = {
                    'id': 0,
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': userInfo.get('email', f'{externalId}@dana.miniapp'),
                    'no_hp': userInfo.get('phone', ''),
                    'external_id': externalId
                }

            # Save DANA tokens if obtained
            if danaAccessToken and user.get('id'):
                try:
                    self.userModel.updateDanaToken(user['id'], {
                        'dana_access_token': danaAccessToken,
                        'dana_external_id': externalId
                    })
                except:
                    pass

            # =============================================================
            # Step 5: Generate JWT token
            # =============================================================
            jwtToken = self._generateJwt(user)

            print(f"[AUTH] Login success! userId={user.get('id')}, dbUser={dbUser}, danaLinked={bool(danaAccessToken)}")

            self.logApiCall('/seamless-login', 'POST',
                           {'external_id': externalId, 'dana_linked': bool(danaAccessToken)},
                           200, {'user_id': user.get('id')})

            responseData = {
                "token": jwtToken,
                "user": {
                    "id": user.get('id'),
                    "name": user.get('nama') or user.get('nama_lengkap') or user.get('full_name'),
                    "email": user.get('email'),
                    "phone": user.get('no_hp') or user.get('handphone'),
                    "external_id": externalId
                },
                "externalId": externalId,
                "dbUser": dbUser,
                "danaLinked": bool(danaAccessToken)
            }

            # Include exchange error for debugging (if DANA API failed but we still proceeded)
            if exchangeError:
                responseData["danaExchangeError"] = exchangeError

            return Response.success(data=responseData, message="Login berhasil")

        except Exception as e:
            print(f"[AUTH] Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response.error(f"Seamless login gagal: {str(e)}", 500)

    # =========================================================================
    # Database
    # =========================================================================

    def _getOrCreateUser(self, externalId, userInfo):
        """
        Search priority:
        1. external_id (returning DANA user)
        2. email (match login server existing)
        3. phone (fallback)
        4. Create new
        """
        try:
            email = userInfo.get('email')
            phone = userInfo.get('phone')
            user = None

            if externalId:
                try:
                    user = self.userModel.findByDanaExternalId(externalId)
                    if user:
                        print(f"[AUTH] Found by external_id: {user.get('id')}")
                except:
                    pass

            if not user and email:
                user = self.userModel.findByEmail(email)
                if user:
                    print(f"[AUTH] Found by email: {user.get('id')} ({email})")

            if not user and phone:
                user = self.userModel.findByPhone(phone)
                if user:
                    print(f"[AUTH] Found by phone: {user.get('id')}")

            if not user:
                print(f"[AUTH] Creating new user: email={email}, phone={phone}")
                userData = {
                    'nama': userInfo.get('name', f'User_{externalId[:8]}'),
                    'email': email or f'{externalId}@dana.miniapp',
                    'no_hp': phone,
                    'external_id': externalId,
                    'dana_external_id': externalId,
                    'created_date': datetime.now(),
                    'is_active': 'Y'
                }
                userId = self.userModel.create(userData)
                user = self.userModel.findById(userId)
            else:
                if not user.get('external_id'):
                    self.userModel.updateExternalId(user['id'], externalId)
                if not user.get('dana_external_id'):
                    try:
                        self.userModel.updateDanaToken(user['id'], {'dana_external_id': externalId})
                    except:
                        pass

            return user

        except Exception as e:
            print(f"[AUTH] Get/Create user error: {str(e)}")
            return None

    # =========================================================================
    # JWT
    # =========================================================================

    def _generateJwt(self, user):
        """Generate JWT token"""
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
                payload = jwt.decode(oldToken, self.jwtSecret, algorithms=['HS256'],
                                    options={"verify_exp": False})
                user = self.userModel.findById(payload.get('user_id'))
                if not user:
                    return Response.error("User tidak ditemukan", 404)

                return Response.success(data={
                    "token": self._generateJwt(user),
                    "expiresIn": self.jwtExpireHours * 3600
                }, message="Token berhasil di-refresh")

            except jwt.InvalidTokenError:
                return Response.error("Token tidak valid", 401)

        except Exception as e:
            return Response.error(f"Refresh token gagal: {str(e)}", 500)

    def generateOauthUrl(self, data):
        """Mini Program pakai my.getAuthCode(), tidak perlu OAuth URL"""
        return Response.success(data={
            "message": "Gunakan my.getAuthCode() di mini app"
        }, message="Mini Program tidak memerlukan OAuth URL")

    def getUserInfo(self, accessToken):
        """Placeholder"""
        return Response.success(data={}, message="Use my.getOpenUserInfo() in mini app")

    # =========================================================================
    # Logging
    # =========================================================================

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
                    json.dumps(responseBody) if isinstance(responseBody, dict) else str(responseBody),
                    datetime.now(),
                    'system'
                ))
                conn.commit()
        except Exception as e:
            print(f"Failed to log: {str(e)}")

    def _maskSensitiveData(self, data):
        """Mask sensitive data"""
        if not data or not isinstance(data, dict):
            return data
        masked = data.copy()
        for key in ['auth_code', 'authCode', 'accessToken', 'refreshToken', 'token']:
            if key in masked and masked[key]:
                value = str(masked[key])
                masked[key] = value[:8] + '***' if len(value) > 8 else '***'
        return masked
