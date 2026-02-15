from flask import Blueprint, request, g
from src.services.auth_service import AuthService
from src.services.dana_auth_service import DanaAuthService
from src.services.dana_payment_service import DanaPaymentService
from src.services.user_service import UserService
from src.services.health_service import HealthService
from src.services.campaign_service import CampaignService
from src.middlewares.auth_middleware import token_required

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
dana_bp = Blueprint('dana', __name__, url_prefix='/api/v1/dana')
user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')
disburse_bp = Blueprint('disburse', __name__, url_prefix='/api/v1/disburse')
campaign_bp = Blueprint('campaign', __name__, url_prefix='/api/v1')

# SNAP API Blueprint (ASPI-mandated path)
snap_bp = Blueprint('snap', __name__, url_prefix='/v1.0')

# Services
authService = AuthService()
danaAuthService = DanaAuthService()
danaPaymentService = DanaPaymentService()
userService = UserService()
healthService = HealthService()
campaignService = CampaignService()


# =============================================================================
# AUTH ROUTES (Tidak perlu bearer token)
# =============================================================================

@auth_bp.route('/generate-oauth-url', methods=['POST'])
def generateOauthUrl():
    """
    Generate DANA OAuth URL
    Catatan: Untuk Mini Program, tidak diperlukan - gunakan my.getAuthCode()
    """
    return danaAuthService.generateOauthUrl(request.json or {})


@auth_bp.route('/apply-token', methods=['POST'])
def applyToken():
    """
    Terima auth code dari Mini App

    Body: { auth_code, external_id }
    """
    return danaAuthService.applyToken(request.json or {})


@auth_bp.route('/seamless-login', methods=['POST'])
def seamlessLogin():
    """
    Seamless login setelah mendapat token dari DANA Mini App

    Body: {
        external_id,
        access_token (optional),
        user_info: { name, phone, email } (optional)
    }
    """
    data = request.json or {}

    # Gunakan DanaAuthService untuk Mini Program
    return danaAuthService.seamlessLogin(data)


@auth_bp.route('/refresh-token', methods=['POST'])
def refreshToken():
    """
    Refresh expired token

    Body: { token } atau { refresh_token }
    """
    return danaAuthService.refreshToken(request.json or {})
    return danaAuthService.refreshToken(request.json or {})


@auth_bp.route('/dana-unbind', methods=['POST'])
@token_required
def unbindDana():
    """
    Unbind/Logout DANA Account
    Headers: Authorization: Bearer <token>
    """
    userId = g.current_user.get('user_id') if hasattr(g, 'current_user') else None
    if not userId:
        return {"status": "error", "message": "Unauthorized"}, 401

    return danaAuthService.unbindAccount(userId)

@auth_bp.route('/finish-redirect', methods=['POST', 'GET'])
def finishRedirect():
    """
    Callback endpoint setelah DANA OAuth redirect
    """
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
def createOrder():
    """
    Create payment order untuk DANA Mini Program

    Body: {
        nominal, email, campaign_id,
        nama_lengkap, doa_muzaki, tipe_zakat, hamba_allah (optional)
    }

    Returns: { orderId } untuk digunakan dengan my.tradePay()
    """
    data = request.json or {}

    # Tambahkan user info dari JWT jika ada token
    authHeader = request.headers.get('Authorization')
    print(f"[API] create-order authHeader: {authHeader}")
    if authHeader and authHeader.startswith('Bearer '):
        try:
            import jwt
            from src.config.config import Config
            token = authHeader.split(' ')[1]
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            data['created_by'] = f"user_{payload.get('user_id')}"
            print(f"[API] Set created_by: {data['created_by']}")
            if not data.get('email'):
                data['email'] = payload.get('email')
            if not data.get('muzaki_id'):
                data['muzaki_id'] = payload.get('muzaki_id')
        except Exception as e:
            print(f"[API] Token decode failed: {str(e)}")
            pass  # Ignore token errors, proceed without user info

    return danaPaymentService.createOrder(data)


@dana_bp.route('/apply-ott', methods=['POST'])
def applyOtt():
    """
    Apply OTT token
    Catatan: Tidak diperlukan untuk Mini Program, my.tradePay() langsung

    Body: { order_id }
    """
    return danaPaymentService.applyOtt(request.json or {})


@dana_bp.route('/history/filter', methods=['GET'])
@token_required
def transactionHistoryFilter():
    """
    Get transaction history
    Headers: Authorization: Bearer <token>
    Query Params: month, year, status, limit, offset
    """
    userId = g.current_user.get('user_id')
    month = request.args.get('month')
    year = request.args.get('year')
    status = request.args.get('status')
    limit = request.args.get('limit', 20)
    offset = request.args.get('offset', 0)

    return danaPaymentService.getHistory(userId, month, year, status, limit, offset)


@dana_bp.route('/status', methods=['POST'])
def checkTransactionStatus():
    """
    Cek status transaksi
    """
    data = request.json or {}
    orderId = data.get('order_id')
    return danaPaymentService.queryPayment(orderId)


@dana_bp.route('/cancel-order', methods=['POST'])
def cancelOrder():
    """
    Cancel order yang belum dibayar

    Body: { order_id, reason (optional) }
    """
    data = request.json or {}
    orderId = data.get('order_id')
    reason = data.get('reason', 'User cancelled')

    if not orderId:
        return {"status": "error", "message": "order_id wajib diisi"}, 400

    return danaPaymentService.cancelOrder(orderId, reason)


@dana_bp.route('/refund-order', methods=['POST'])
@token_required
def refundOrder():
    """
    Refund order (Admin only recommended, but here restricted by token)
    Body: { order_id, reason }
    """
    # Authorization check could be added here (e.g. check if user is admin)
    data = request.json or {}
    orderId = data.get('order_id')
    reason = data.get('reason', 'Refund request')

    if not orderId:
        return {"status": "error", "message": "order_id wajib diisi"}, 400

    return danaPaymentService.refundOrder(orderId, reason)


@dana_bp.route('/balance-inquiry', methods=['GET'])
@token_required
def balanceInquiry():
    """
    Cek saldo DANA User
    Headers: Authorization: Bearer <token>
    """
    userId = g.current_user.get('user_id') if hasattr(g, 'current_user') else None
    if not userId:
        return {"status": "error", "message": "Unauthorized"}, 401

    return danaPaymentService.balanceInquiry(userId)


@dana_bp.route('/history', methods=['GET'])
@token_required
def transactionHistory():
    """
    Get DANA Transaction History
    Params: page, pageSize
    """
    userId = g.current_user.get('user_id')
    print(f"DEBUG HISTORY: userId={userId} type={type(userId)}")
    if userId is None:
        return {"status": "error", "message": "Unauthorized"}, 401
    
    page = request.args.get('page', 1)
    pageSize = request.args.get('pageSize', 10)
    
    return danaPaymentService.transactionHistory(userId, page, pageSize)


@dana_bp.route('/history/<refNo>', methods=['GET'])
@token_required
def transactionDetail(refNo):
    """
    Get DANA Transaction Detail
    """
    userId = g.current_user.get('user_id')
    if userId is None:
        return {"status": "error", "message": "Unauthorized"}, 401
        
    return danaPaymentService.transactionDetail(userId, refNo)


@dana_bp.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint untuk menerima notifikasi dari DANA

    DANA akan mengirim notifikasi saat status pembayaran berubah
    """
    signature = request.headers.get('X-SIGNATURE')
    headers = {
        'X-SIGNATURE': signature,
        'X-TIMESTAMP': request.headers.get('X-TIMESTAMP'),
        'Content-Type': request.headers.get('Content-Type')
    }
    return danaPaymentService.webhook(request.json or {}, signature, headers)


@dana_bp.route('/finish-payment', methods=['POST', 'GET'])
def finishPayment():
    """
    Callback setelah user selesai di halaman DANA
    """
    data = {}
    if request.method == 'GET':
        data = {
            'orderId': request.args.get('orderId'),
            'resultCode': request.args.get('resultCode'),
            'resultStatus': request.args.get('resultStatus')
        }
    else:
        data = request.json or {}

    return danaPaymentService.finishPayment(data)


# =============================================================================
# USER ROUTES (Perlu bearer token)
# =============================================================================

@user_bp.route('/profile', methods=['GET'])
@token_required
def getProfile():
    """
    Get user profile
    Headers: Authorization: Bearer <token>
    """
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


# =============================================================================
# SNAP API ROUTES (ASPI-mandated paths)
# Sesuai dokumentasi DANA untuk Finish Notify
# =============================================================================

@snap_bp.route('/debit/notify', methods=['POST'])
def debitNotify():
    """
    SNAP API Finish Notify Endpoint

    Path: /v1.0/debit/notify (ASPI-mandated format)

    DANA akan mengirim notifikasi pembayaran ke endpoint ini.
    Headers:
    - X-SIGNATURE: Digital signature untuk verifikasi
    - X-TIMESTAMP: Timestamp request

    Body (FinishNotifyRequest):
    {
        "originalPartnerReferenceNo": "partner_ref",
        "originalReferenceNo": "dana_ref",
        "merchantId": "merchant_id",
        "amount": { "value": "10000.00", "currency": "IDR" },
        "latestTransactionStatus": "SUCCESS",
        "transactionStatusDesc": "Payment successful"
    }
    """
    signature = request.headers.get('X-SIGNATURE')
    headers = {
        'X-SIGNATURE': signature,
        'X-TIMESTAMP': request.headers.get('X-TIMESTAMP'),
        'Content-Type': request.headers.get('Content-Type')
    }
    return danaPaymentService.webhook(request.json or {}, signature, headers)


@snap_bp.route('/debit/status', methods=['POST'])
def debitStatus():
    """
    SNAP API Query Payment Status

    Path: /v1.0/debit/status

    Body:
    {
        "originalPartnerReferenceNo": "partner_ref",
        "originalReferenceNo": "dana_ref",
        "merchantId": "merchant_id"
    }
    """
    data = request.json or {}
    orderId = data.get('originalPartnerReferenceNo') or data.get('partnerReferenceNo')

    if not orderId:
        return {
            "responseCode": "4005401",
            "responseMessage": "Invalid Mandatory Field originalPartnerReferenceNo"
        }, 400

    result = danaPaymentService.queryPayment(orderId)

    # Convert to SNAP API format
    if result.get('status') == 'success':
        paymentData = result.get('data', {})
        return {
            "responseCode": "2005400",
            "responseMessage": "Successful",
            "originalPartnerReferenceNo": paymentData.get('orderId'),
            "originalReferenceNo": paymentData.get('danaReferenceNo'),
            "latestTransactionStatus": paymentData.get('status', '').upper(),
            "amount": {
                "value": str(paymentData.get('amount', 0)),
                "currency": "IDR"
            }
        }, 200
    else:
        return {
            "responseCode": "4045401",
            "responseMessage": "Transaction Not Found"
        }, 404


# =============================================================================
# CAMPAIGN ROUTES (Menggantikan external API cintazakat.id)
# =============================================================================

@campaign_bp.route('/kegiatan/index', methods=['POST'])
def campaignIndex():
    """
    List semua campaign/program
    
    Body: {
        limit: 20,
        offset: 0,
        tipe: "zakat",  // optional
        institusi: "BAZNAS",  // optional
        kategori: "Pendidikan",  // optional
        sort: "terbaru"  // optional
    }
    """
    data = request.get_json(silent=True) or request.form
    return campaignService.getCampaigns(data)


@campaign_bp.route('/kegiatan/search', methods=['POST'])
def campaignSearch():
    """
    Search kegiatan
    
    Body: {
        keyword: "zakat",
        limit: 20,
        offset: 0
    }
    """
    data = request.get_json(silent=True) or request.form
    return campaignService.searchCampaigns(data)


@campaign_bp.route('/kegiatan/detail', methods=['POST'])
def campaignDetail():
    """
    Detail kegiatan
    
    Body: {
        id: "1"
    }
    """
    data = request.get_json(silent=True) or request.form
    return campaignService.getCampaignDetail(data)


@campaign_bp.route('/listfilter/byinstitusi', methods=['POST'])
def filterByInstitution():
    """
    Filter institusi
    """
    return campaignService.getInstitutions()


@campaign_bp.route('/listfilter/bycategory', methods=['POST'])
def filterByCategory():
    """
    Filter kategori
    """
    return campaignService.getCategories()


# =============================================================================
# CONTENT ROUTES (Banner, FAQ, Tentang, dll)
# =============================================================================

@campaign_bp.route('/banner/index', methods=['POST'])
def bannerList():
    """
    List banner
    TODO: Implement BannerService if needed, for now mock response
    """
    # TODO: Implement banner service jika ada tabel banner
    return {
        'code': 200,
        'message': 'Success',
        'results': []
    }, 200


@campaign_bp.route('/faq/index', methods=['POST'])
def faqList():
    """
    List FAQ
    TODO: Implement FaqService
    """
    # TODO: Implement FAQ service jika ada tabel FAQ
    return {
        'code': 200,
        'message': 'Success',
        'results': []
    }, 200


@campaign_bp.route('/tentang/index', methods=['POST'])
def tentangKami():
    """
    Tentang Kami
    """
    # TODO: Implement tentang service
    return {
        'code': 200,
        'message': 'Success',
        'results': {
            'judul': 'Tentang Kami',
            'deskripsi': 'Informasi tentang organisasi'
        }
    }, 200


@campaign_bp.route('/tentang/syaratketentuan', methods=['POST'])
def syaratKetentuan():
    """
    Syarat & Ketentuan
    """
    # TODO: Implement syarat ketentuan service
    return {
        'code': 200,
        'message': 'Success',
        'results': {
            'judul': 'Syarat dan Ketentuan',
            'deskripsi': 'Syarat dan ketentuan penggunaan'
        }
    }, 200


@campaign_bp.route('/contact/index', methods=['POST'])
def contactIndex():
    """
    Contact Info
    """
    # TODO: Implement contact service
    return {
        'code': 200,
        'message': 'Success',
        'results': {
            'email': 'info@example.com',
            'phone': '021-12345678',
            'address': 'Jakarta, Indonesia'
        }
    }, 200


@campaign_bp.route('/sendmessage', methods=['POST'])
def sendMessage():
    """
    Send Message
    
    Body: {
        name: "Nama",
        email: "email@example.com",
        message: "Pesan"
    }
    """
    # TODO: Implement send message service
    data = request.get_json(silent=True) or request.form
    return {
        'code': 200,
        'message': 'Pesan berhasil dikirim',
        'results': None
    }, 200
