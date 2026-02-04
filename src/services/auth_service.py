import uuid
import jwt
from datetime import datetime, timedelta
from src.models.user_model import UserModel
from src.models.muzaki_model import MuzakiModel
from src.utils.response import Response
from src.config.config import Config

class AuthService:
    """
    Service untuk autentikasi termasuk DANA seamless login
    """

    def __init__(self):
        self.userModel = UserModel()
        self.muzakiModel = MuzakiModel()
        self.jwtSecret = getattr(Config, 'JWT_SECRET', 'your-secret-key-change-in-production')
        self.jwtExpireHours = getattr(Config, 'JWT_EXPIRE_HOURS', 24)

    def seamlessLogin(self, data):
        """
        Seamless login untuk user DANA
        Menerima data dari DANA OAuth callback dan membuat/update user

        Args:
            data: dict containing:
                - auth_code: Authorization code dari DANA
                - access_token: Access token dari DANA (setelah apply token)
                - refresh_token: Refresh token dari DANA
                - expires_in: Token expiry time in seconds
                - external_id: External ID dari OAuth flow
                - user_info: Optional user info dari DANA (nama, phone, dll)
        """
        try:
            accessToken = data.get('access_token')
            refreshToken = data.get('refresh_token')
            externalId = data.get('external_id')
            expiresIn = data.get('expires_in', 94608000)  # Default 3 tahun
            userInfo = data.get('user_info', {})

            if not accessToken:
                return Response.error("Access token is required", 400)

            # Generate unique email untuk user DANA jika tidak ada info
            danaUserId = userInfo.get('user_id') or externalId or str(uuid.uuid4())[:12]
            email = userInfo.get('email') or f"dana_{danaUserId}@dana.user"
            nama = userInfo.get('name') or userInfo.get('fullName') or 'DANA User'
            handphone = userInfo.get('phone') or userInfo.get('mobileNumber') or ''

            # Cari user existing berdasarkan email atau dana_external_id
            user = self.userModel.findByEmailAndType(email, 'user')

            if not user and externalId:
                # Coba cari berdasarkan external_id
                user = self.userModel.findByDanaExternalId(externalId)

            if not user:
                # Buat user baru
                userId = self.userModel.create({
                    'email': email,
                    'password': '',  # DANA user tidak pakai password
                    'tipe': 'user',
                    'full_name': nama,
                    'handphone': handphone,
                    'dana_access_token': accessToken,
                    'dana_refresh_token': refreshToken,
                    'dana_external_id': externalId,
                    'dana_user_id': danaUserId,
                    'dana_token_expires_at': datetime.now() + timedelta(seconds=expiresIn),
                    'dana_linked_at': datetime.now()
                })
                user = self.userModel.findById(userId)
            else:
                # Update token untuk user existing
                self.userModel.updateDanaToken(user['id'], {
                    'dana_access_token': accessToken,
                    'dana_refresh_token': refreshToken,
                    'dana_token_expires_at': datetime.now() + timedelta(seconds=expiresIn),
                    'dana_external_id': externalId,
                    'dana_user_id': danaUserId
                })
                # Refresh user data
                user = self.userModel.findById(user['id'])

            # Cari atau buat muzaki
            muzaki = self.muzakiModel.findByEmail(email)
            if not muzaki:
                muzakiId = self.muzakiModel.create({
                    'email': email,
                    'nama': nama,
                    'tipe': 'perorangan',
                    'handphone': handphone,
                    'npwz': '',
                    'kode_institusi': 'PUSAT',
                    'alamat': '',
                    'created_by': 'dana_seamless'
                })
                muzaki = self.muzakiModel.findById(muzakiId)

                # Link user dengan muzaki
                if muzaki:
                    self.userModel.updateMuzakiId(user['id'], muzaki['id'])

            # Generate JWT token untuk session
            jwtPayload = {
                'user_id': user['id'],
                'email': email,
                'muzaki_id': muzaki['id'] if muzaki else None,
                'type': 'dana_user',
                'exp': datetime.utcnow() + timedelta(hours=self.jwtExpireHours),
                'iat': datetime.utcnow()
            }
            sessionToken = jwt.encode(jwtPayload, self.jwtSecret, algorithm='HS256')

            return Response.success(data={
                "token": sessionToken,
                "token_type": "Bearer",
                "expires_in": self.jwtExpireHours * 3600,
                "user": {
                    "id": user['id'],
                    "email": email,
                    "name": nama,
                    "phone": handphone
                },
                "muzaki_id": muzaki['id'] if muzaki else None,
                "npwz": muzaki.get('npwz', '') if muzaki else '',
                "dana_linked": True
            }, message="Seamless login berhasil")

        except Exception as e:
            return Response.error(f"Seamless login gagal: {str(e)}", 500)

    def verifyToken(self, token):
        """
        Verifikasi JWT token dan return payload
        """
        try:
            payload = jwt.decode(token, self.jwtSecret, algorithms=['HS256'])
            return Response.success(data=payload)
        except jwt.ExpiredSignatureError:
            return Response.error("Token sudah expired", 401)
        except jwt.InvalidTokenError as e:
            return Response.error(f"Token tidak valid: {str(e)}", 401)

    def getDanaAccessToken(self, userId):
        """
        Ambil DANA access token untuk user
        Digunakan untuk API call ke DANA
        """
        user = self.userModel.findById(userId)
        if not user:
            return None

        # Cek apakah token masih valid
        expiresAt = user.get('dana_token_expires_at')
        if expiresAt and datetime.now() > expiresAt:
            # Token expired, perlu refresh
            # TODO: Implement refresh token logic
            return None

        return user.get('dana_access_token')

    def refreshDanaToken(self, userId):
        """
        Refresh DANA token menggunakan refresh_token
        TODO: Implement this when needed
        """
        pass

    def logout(self, userId):
        """
        Logout user - invalidate token
        """
        try:
            # Bisa tambahkan logic untuk blacklist token jika perlu
            return Response.success(message="Logout berhasil")
        except Exception as e:
            return Response.error(f"Logout gagal: {str(e)}", 500)
