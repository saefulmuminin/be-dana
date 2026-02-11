"""
DANA Mini Program Authentication Service (MINI_DANA)

Flow (Partner Webview Onboarding):
1. Mini app call my.getAuthCode({ scopes: ['MINI_PROGRAM','CASHIER','QUERY_BALANCE','DEFAULT_BASIC_PROFILE','MINI_DANA','PUBLIC_ID','KYC_INFO'] })
2. Mini app kirim authCode ke backend
3. Backend exchange authCode ke DANA Apply Token API -> dapat accessToken
   - Ref: https://dashboard.dana.id/api-docs/read/110
4. Backend call Query User Profile API (BE-to-BE) -> dapat USER_LOGIN_ID, dll
   - Ref: https://dashboard.dana.id/api-docs/read/38
5. Backend create/find user di database -> generate JWT
6. Return JWT token ke mini app

API Reference:
- Apply Token: POST /v1/authorizations/applyToken
- Query User Profile: POST /v1.0/emoney/queryUserProfile
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

    def _generateSignatureCustom(self, stringToSign):
        """Generate RSA signature (PKCS1_v1_5 + SHA256) for custom string"""
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
                privateKey = f"-----BEGIN PRIVATE KEY-----\n{formattedKey}\n-----END PRIVATE KEY-----"

             pkey = RSA.importKey(privateKey)
             signer = PKCS1_v1_5.new(pkey)
             digest = SHA256.new()
             digest.update(stringToSign.encode('utf-8'))
             return base64.b64encode(signer.sign(digest)).decode('utf-8')

        except Exception as e:
            print(f"[AUTH] Custom Signature failed: {str(e)}")
            return None

    def _exchangeAuthCode(self, authCode):
        """
        Exchange authCode dari my.getAuthCode() -> accessToken via DANA Apply Token API
        POST /v1/authorizations/applyToken
        Ref: https://dashboard.dana.id/api-docs/read/110
        """
        try:
            # Revert to DANA Widget/Legacy URL because Client ID is from DANA Dashboard
            # Antom URL rejected the Client ID.
            # We suspect previous 404 was due to wrong path on api.sandbox.dana.id
            
            baseUrl = Config.DANA_WIDGET_BASE_URL # https://api.sandbox.dana.id
            print(f"[DEBUG] Using DANA_WIDGET_BASE_URL = {baseUrl}")

            # Correct Endpoint for DANA V2/Widget Binding might be:
            # /dana/oauth/auth/applyToken.htm (Common for legacy)
            # OR standard /v1/authorizations/applyToken BUT with correct formatting?
            # Let's try the path documented for Widget: /dana/oauth/auth/applyToken.htm
            # DANA Indonesia SNAP API
            # Endpoint: /v1.0/authorizations/applyToken
            # Standard JSON format (Not envelope)
            
            # DANA SNAP API (B2B2C Binding)
            # Endpoint: /v1.0/access-token/b2b2c.htm
            # Ref: User provided documentation
            
            endpoint = "/v1.0/access-token/b2b2c.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')

            originalPartnerId = Config.DANA_CLIENT_ID # Client ID / X-PARTNER-ID

            requestBody = {
                "grantType": "AUTHORIZATION_CODE",
                "authCode": authCode,
                "refreshToken": "",
                "additionalInfo": {}
            }
            
            # Signature for SNAP API
            # StringToSign = client_ID + "|" + X-TIMESTAMP (Based on user doc? Wait, user doc says:)
            # "X-SIGNATURE: asymmetric signature SHA256withRSA(Private_Key, stringToSign)"
            # "Where: stringToSign = client_ID + “|” + X-TIMESTAMP"
            # WAIT! The string to sign is JUST "client_ID|timestamp" ???
            # Let's check the doc carefully.
            # "stringToSign = client_ID + “|” + X-TIMESTAMP" -> This looks like a specific format for this API?
            # BUT standard SNAP usually uses HTTP Method + Endpoint + Body + Timestamp.
            # Let's check if there's a specific instruction. 
            # The doc provided says: "Where: stringToSign = client_ID + “|” + X-TIMESTAMP" under the Request Sample.
            # This is VERY different from standard SNAP. I will try this specific signature first.

            stringToSign = f"{originalPartnerId}|{timestamp}"
            
            # However, `_generateSignature` method implements standard SNAP signature (Method:Endpoint:BodyHash:Timestamp).
            # If I need to sign "client_ID|timestamp", I need to construct it manually or modify/bypass `_generateSignature`.
            
            # Let's try to generate signature manually here to be safe
            signature = self._generateSignatureCustom(stringToSign)

            if not signature:
                 # Fallback to standard if custom fails (unlikely if logic is right)
                 return {'success': False, 'error': 'Signature generation failed'}

            headers = {
                'Content-Type': 'application/json',
                'X-TIMESTAMP': timestamp,
                'X-CLIENT-KEY': originalPartnerId,
                'X-PARTNER-ID': originalPartnerId,
                'X-SIGNATURE': signature
            }

            print(f"[AUTH] Exchange authCode -> {fullUrl}")
            # print(f"[AUTH] Payload: {json.dumps(requestBody)}")
            # print(f"[AUTH] StringToSign: {stringToSign}")

            response = requests.post(fullUrl, json=requestBody, headers=headers, timeout=30)
            print(f"[AUTH] DANA token response: {response.status_code} -> {response.text[:300]}")

            self.logApiCall(endpoint, 'POST', {'authCode': authCode[:10] + '***'},
                           response.status_code, response.text[:500])

            if response.ok:
                respData = response.json()

                # Response Codes:
                # 2007400: Successful
                
                responseCode = respData.get('responseCode', '')
                responseMessage = respData.get('responseMessage', '')

                isSuccess = (responseCode == '2007400')

                if isSuccess:
                    accessToken = respData.get('accessToken')
                    print(f"[AUTH] Got accessToken!")
                    
                    # Parse Additional Info for User ID
                    # "additionalInfo": { "userInfo": { "publicUserId": "..." } }
                    additionalInfo = respData.get('additionalInfo', {})
                    userInfoDict = additionalInfo.get('userInfo', {})
                    publicUserId = userInfoDict.get('publicUserId', '')

                    return {
                        'success': True,
                        'accessToken': accessToken,
                        'refreshToken': respData.get('refreshToken'),
                        'expiresIn': 0, # usually long lived
                        'accessTokenExpiryTime': respData.get('accessTokenExpiryTime'),
                        'userLoginId': publicUserId # Use Public User ID as login ID
                    }
                else:
                    return {'success': False, 'error': f"{responseCode}: {responseMessage}"}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"[AUTH] Exchange failed: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _queryUserProfile(self, accessToken):
        """
        Query User Profile dari DANA (DANA Widget API)
        Endpoint: /dana/member/query/queryUserProfile.htm
        Ref: Official DANA Documentation provided by user
        """
        try:
            baseUrl = Config.DANA_WIDGET_BASE_URL
            endpoint = "/dana/member/query/queryUserProfile.htm"
            fullUrl = f"{baseUrl}{endpoint}"

            jakartaTz = timezone(timedelta(hours=7))
            timestamp = datetime.now(jakartaTz).strftime('%Y-%m-%dT%H:%M:%S+07:00')
            reqMsgId = str(uuid.uuid4()).replace('-', '')

            # Request Body sesuai dokumentasi DANA Widget API
            # NOTE: Order of keys might matter for signature if we just dump the dict.
            # User script uses: client_id, client_secret, access_token, reqTime, reqMsgId. 
            # We follow that implicit structure.
            requestPayload = {
                "request": {
                    "head": {
                        "version": "2.0",
                        "function": "dana.member.query.queryUserProfile",
                        "clientId": Config.DANA_CLIENT_ID,
                        "clientSecret": Config.DANA_CLIENT_SECRET,
                        "reqTime": timestamp,
                        "reqMsgId": reqMsgId,
                        "accessToken": accessToken,
                        "reserve": "{}"
                    },
                    "body": {
                        "userResources": [
                            "BALANCE",         # Added by user request
                            "LOGIN_ID",        # Phone number
                            "NICKNAME",        # Nickname
                            "FULLNAME",        # Full name
                            "EMAIL",           # Email
                            "AVATAR_URL",      # Azure/Avatar URL
                            "MASK_DANA_ID",    # Masked ID
                            "PUBLIC_USER_ID"   # Public ID if available
                        ]
                    }
                },
                "signature": ""  # Signature generated below
            }

            # Generate Signature based on 'request' object (excluding signature field itself)
            # Experiment v1.6: Ensure the payload on the wire matches the signed string EXACTLY.
            # Convert to Minified JSON for signing.
            
            requestBodyStr = json.dumps(requestPayload['request'], separators=(',', ':'))
            print(f"[DEBUG] StringToSign (QueryProfile): {requestBodyStr}")

            # 2. Sign it using the custom signer (which does SHA256withRSA)
            signature = self._generateSignatureCustom(requestBodyStr)
            
            if signature:
                requestPayload['signature'] = signature

            headers = {
                'Content-Type': 'application/json',
                # Beaver/X-Signature headers mungkin tidak diperlukan jika signature masuk body?
                # Tapi kita keep header standard untuk keamanan trace log
                'X-TIMESTAMP': timestamp,
                'X-CLIENT-KEY': Config.DANA_CLIENT_ID,
            }

            print(f"[AUTH] Query User Profile (Widget API) -> {fullUrl}")
            
            # Serialize the FINAL payload to minified string as well
            finalPayloadStr = json.dumps(requestPayload, separators=(',', ':'))
            # print(f"[AUTH] Payload: {finalPayloadStr}") 

            # Use data=finalPayloadStr to prevent requests from adding spaces
            response = requests.post(fullUrl, data=finalPayloadStr, headers=headers, timeout=30)
            print(f"[AUTH] User profile response ({response.status_code}): {response.text[:1000]}")

            self.logApiCall(endpoint, 'POST', {'token': '***'},
                           response.status_code, response.text[:500])

            if response.ok:
                respJson = response.json()
                responseBody = respJson.get('response', {})
                bodyData = responseBody.get('body', {})
                resultInfo = bodyData.get('resultInfo', {})
                
                resultCode = resultInfo.get('resultCode', '')
                resultStatus = resultInfo.get('resultStatus', '')

                isSuccess = (resultStatus == 'S' or resultCode == 'SUCCESS')

                if not isSuccess:
                    return {'success': False, 'error': f"{resultCode}: {resultInfo.get('resultMsg')}"}

                # Parse userResourceInfos
                userResources = bodyData.get('userResourceInfos', [])
                parsedData = {}
                
                for item in userResources:
                    rType = item.get('resourceType')
                    rValue = item.get('value')
                    parsedData[rType] = rValue

                # Map to internal format
                userLoginId = parsedData.get('LOGIN_ID', '')
                name = parsedData.get('NICKNAME') or parsedData.get('FULLNAME') or ''
                email = parsedData.get('EMAIL', '')
                # Kadang Avatar URL ada di AVATAR_URL
                avatar = parsedData.get('AVATAR_URL', '')

                print(f"[AUTH] Parsed Widget Profile: ID={userLoginId}, Name={name}, Email={email}")

                return {
                    'success': True,
                    'userLoginId': userLoginId,
                    'phone': userLoginId,
                    'email': email,
                    'name': name,
                    'publicUserId': parsedData.get('PUBLIC_USER_ID', ''),
                    'avatar': avatar,
                    'raw': respJson
                }
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"[AUTH] Query user profile failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Main Auth Endpoints
    # =========================================================================

    def applyToken(self, data):
        """Terima auth code dari Mini App"""
        try:
            authCode = data.get('auth_code') or data.get('authCode') or data.get('authcode')
            externalId = data.get('external_id') or data.get('externalId') or str(uuid.uuid4())

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
        Seamless Login - Exchange authCode, Query User Profile (BE-to-BE), generate JWT

        Flow (Partner Webview Onboarding):
        1. Terima authCode dari frontend (dari my.getAuthCode)
        2. Exchange authCode ke DANA Apply Token API -> accessToken + userLoginId
        3. Query User Profile (BE-to-BE) -> USER_LOGIN_ID, data lengkap
        4. Create/find user di database
        5. Return JWT token
        """
        try:
            externalId = data.get('external_id') or str(uuid.uuid4())
            authCode = data.get('auth_code')
            frontendUserInfo = data.get('user_info') or {}

            print(f"[AUTH] === Seamless Login (MINI_DANA) ===")
            print(f"[AUTH] SERVICE VERSION: v1.7-pkcs8-key")
            print(f"[AUTH] externalId: {externalId}")
            print(f"[AUTH] hasAuthCode: {bool(authCode)}")

            if not authCode:
                return Response.error("auth_code wajib diisi. Gunakan my.getAuthCode() di mini app.", 400)

            # =============================================================
            # Step 1: Exchange authCode -> accessToken via Apply Token API
            # =============================================================
            danaUserInfo = {}
            danaAccessToken = None
            exchangeError = None

            print(f"[AUTH] Step 1: Exchanging authCode with DANA Apply Token API...")

            tokenResult = self._exchangeAuthCode(authCode)

            if tokenResult.get('success'):
                danaAccessToken = tokenResult.get('accessToken')
                userLoginId = tokenResult.get('userLoginId', '')
                print(f"[AUTH] accessToken obtained: {danaAccessToken[:20]}...")
                if userLoginId:
                    print(f"[AUTH] userLoginId from Apply Token: {userLoginId}")

                # =============================================================
                # Step 2: Query User Profile (BE-to-BE) untuk data lengkap
                # =============================================================
                print(f"[AUTH] Step 2: Querying User Profile (BE-to-BE)...")
                profileResult = self._queryUserProfile(danaAccessToken)

                if profileResult.get('success'):
                    danaUserInfo = {
                        'phone': profileResult.get('userLoginId') or profileResult.get('phone') or userLoginId,
                        'email': profileResult.get('email', ''),
                        'name': profileResult.get('name', ''),
                        'publicUserId': profileResult.get('publicUserId', '')
                    }
                    print(f"[AUTH] DANA profile: userLoginId={danaUserInfo['phone']}, email={danaUserInfo['email']}")
                else:
                    # Fallback: gunakan userLoginId dari Apply Token response
                    print(f"[AUTH] Profile query failed: {profileResult.get('error')} - using Apply Token data")
                    if userLoginId:
                        danaUserInfo = {
                            'phone': '',
                            'email': '',
                            'name': '',
                            'publicUserId': userLoginId
                        }
            else:
                exchangeError = f"Token exchange failed: {tokenResult.get('error')}"
                print(f"[AUTH] {exchangeError} - using frontend info as fallback")

            # =============================================================
            # Step 3: Merge user info (DANA API data > frontend data)
            # =============================================================
            userInfo = {
                'name': danaUserInfo.get('name') or frontendUserInfo.get('name', ''),
                'phone': danaUserInfo.get('phone') or frontendUserInfo.get('phone', ''),
                'email': danaUserInfo.get('email') or frontendUserInfo.get('email', ''),
                'publicUserId': danaUserInfo.get('publicUserId', '')
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
                        'dana_refresh_token': tokenResult.get('refreshToken'),
                        'dana_token_expires_at': tokenResult.get('accessTokenExpiryTime'),
                        'dana_external_id': externalId,
                        'dana_user_id': userInfo.get('publicUserId') or userInfo.get('phone')
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
        return Response.success(data={}, message="Use QueryUserProfile API (BE-to-BE)")

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
