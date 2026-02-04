from flask import Blueprint, request, g
from src.services.auth_service import AuthService
from src.services.dana_auth_service import DanaAuthService
from src.services.dana_payment_service import DanaPaymentService
from src.services.user_service import UserService
from src.services.health_service import HealthService
from src.middlewares.auth_middleware import token_required

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
dana_bp = Blueprint('dana', __name__, url_prefix='/api/v1/dana')
user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')
disburse_bp = Blueprint('disburse', __name__, url_prefix='/api/v1/disburse')

# Services
authService = AuthService()
danaAuthService = DanaAuthService()
danaPaymentService = DanaPaymentService()
userService = UserService()
healthService = HealthService()


# =============================================================================
# AUTH ROUTES
# =============================================================================

@auth_bp.route('/generate-oauth-url', methods=['POST'])
def generateOauthUrl():
    """
    Generate DANA OAuth URL untuk seamless login
    Body: { redirect_url, mobile_number (optional), external_id (optional) }
    """
    return danaAuthService.generateOauthUrl(request.json or {})


@auth_bp.route('/apply-token', methods=['POST'])
def applyToken():
    """
    Exchange auth code untuk access token
    Body: { auth_code, external_id }
    """
    return danaAuthService.applyToken(request.json or {})


@auth_bp.route('/seamless-login', methods=['POST'])
def seamlessLogin():
    """
    Seamless login setelah mendapat token dari DANA
    Body: {
        access_token, refresh_token, expires_in,
        external_id, user_info: { name, phone, email }
    }
    """
    data = request.json or {}
    return authService.seamlessLogin(data)


@auth_bp.route('/refresh-token', methods=['POST'])
def refreshToken():
    """
    Refresh expired access token
    Body: { refresh_token, external_id }
    """
    return danaAuthService.refreshToken(request.json or {})


@auth_bp.route('/finish-redirect', methods=['POST', 'GET'])
def finishRedirect():
    """
    Callback endpoint setelah DANA OAuth redirect
    """
    # Bisa handle query params dari GET atau body dari POST
    authCode = request.args.get('authCode') or (request.json or {}).get('authCode')
    externalId = request.args.get('externalId') or (request.json or {}).get('externalId')

    return {
        "status": "success",
        "message": "Redirect callback received",
        "data": {
            "authCode": authCode,
            "externalId": externalId
        }
    }, 200


@auth_bp.route('/health', methods=['GET'])
def healthCheck():
    """
    Health check endpoint
    """
    return healthService.getHealthStatus()


# =============================================================================
# DANA PAYMENT ROUTES
# =============================================================================

@dana_bp.route('/create-order', methods=['POST'])
@token_required
def createOrder():
    """
    Create payment order di DANA
    Headers: Authorization: Bearer <token>
    Body: {
        access_token (DANA token),
        nominal, email, campaign_id,
        nama_lengkap, doa_muzaki, tipe_zakat, hamba_allah (optional)
    }
    """
    data = request.json or {}

    # Tambahkan user info dari JWT jika ada
    if hasattr(g, 'current_user'):
        data['created_by'] = f"user_{g.current_user.get('user_id')}"
        if not data.get('email'):
            data['email'] = g.current_user.get('email')
        if not data.get('muzaki_id'):
            data['muzaki_id'] = g.current_user.get('muzaki_id')

    return danaPaymentService.createOrder(data)


@dana_bp.route('/apply-ott', methods=['POST'])
@token_required
def applyOtt():
    """
    Apply OTT token untuk pembayaran
    Headers: Authorization: Bearer <token>
    Body: { access_token (DANA token), order_id }
    """
    return danaPaymentService.applyOtt(request.json or {})


@dana_bp.route('/query-payment/<orderId>', methods=['GET'])
@token_required
def queryPayment(orderId):
    """
    Query status pembayaran dari DANA
    Headers: Authorization: Bearer <token>
    """
    return danaPaymentService.queryPayment(orderId)


@dana_bp.route('/cancel-order', methods=['POST'])
@token_required
def cancelOrder():
    """
    Cancel order yang belum dibayar
    Headers: Authorization: Bearer <token>
    Body: { order_id, reason (optional) }
    """
    data = request.json or {}
    orderId = data.get('order_id')
    reason = data.get('reason', 'User cancelled')

    if not orderId:
        return {"status": "error", "message": "order_id wajib diisi"}, 400

    return danaPaymentService.cancelOrder(orderId, reason)


@dana_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint untuk menerima notifikasi dari DANA
    Tidak perlu auth karena dipanggil oleh DANA server
    """
    # Ambil signature dari header untuk validasi
    signature = request.headers.get('X-SIGNATURE')
    return danaPaymentService.webhook(request.json or {}, signature)


@dana_bp.route('/finish-payment', methods=['POST', 'GET'])
def finishPayment():
    """
    Callback setelah user selesai di halaman DANA
    """
    orderId = request.args.get('orderId') or (request.json or {}).get('orderId')
    status = request.args.get('status') or (request.json or {}).get('status')

    return {
        "status": "success",
        "message": "Payment finished",
        "data": {
            "orderId": orderId,
            "paymentStatus": status
        }
    }, 200


# =============================================================================
# USER ROUTES
# =============================================================================

@user_bp.route('/profile', methods=['GET'])
@token_required
def getProfile():
    """
    Get user profile
    Headers: Authorization: Bearer <token>
    """
    # Ambil user info dari JWT token (di-set oleh middleware)
    userId = g.current_user.get('user_id') if hasattr(g, 'current_user') else None
    muzakiId = g.current_user.get('muzaki_id') if hasattr(g, 'current_user') else None
    email = g.current_user.get('email') if hasattr(g, 'current_user') else None

    return userService.getProfile(userId=userId, email=email, muzakiId=muzakiId)


@user_bp.route('/profile', methods=['PUT'])
@token_required
def updateProfile():
    """
    Update user profile
    Headers: Authorization: Bearer <token>
    Body: { nama, handphone, alamat, tgl_lahir, jenis_kelamin }
    """
    muzakiId = g.current_user.get('muzaki_id') if hasattr(g, 'current_user') else None

    if not muzakiId:
        return {"status": "error", "message": "Muzaki not linked"}, 400

    data = request.json or {}
    return userService.updateProfile(muzakiId, data)


@user_bp.route('/transaction-history', methods=['GET'])
@token_required
def transactionHistory():
    """
    Get transaction history
    Headers: Authorization: Bearer <token>
    Query: limit, offset (optional)
    """
    userId = g.current_user.get('user_id') if hasattr(g, 'current_user') else None
    muzakiId = g.current_user.get('muzaki_id') if hasattr(g, 'current_user') else None
    email = g.current_user.get('email') if hasattr(g, 'current_user') else None

    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    return userService.getTransactionHistory(
        userId=userId, email=email, muzakiId=muzakiId,
        limit=limit, offset=offset
    )


@user_bp.route('/transaction-detail/<transaction_id>', methods=['GET'])
@token_required
def transactionDetail(transaction_id):
    """
    Get transaction detail
    Headers: Authorization: Bearer <token>
    """
    userId = g.current_user.get('user_id') if hasattr(g, 'current_user') else None
    return userService.getTransactionDetail(transaction_id, userId)


@user_bp.route('/send-history-email', methods=['POST'])
@token_required
def sendHistoryEmail():
    """
    Send transaction history to email
    Headers: Authorization: Bearer <token>
    Body: { email (optional, default from token) }
    """
    email = (request.json or {}).get('email')
    muzakiId = g.current_user.get('muzaki_id') if hasattr(g, 'current_user') else None

    if not email and hasattr(g, 'current_user'):
        email = g.current_user.get('email')

    if not email:
        return {"status": "error", "message": "Email wajib diisi"}, 400

    return userService.sendHistoryEmail(email, muzakiId)


# =============================================================================
# DISBURSE ROUTES
# =============================================================================

@disburse_bp.route('/notify', methods=['POST'])
def disburseNotify():
    """
    Webhook untuk notifikasi disbursement
    """
    return {"status": "success", "message": "Disburse notification received"}, 200
