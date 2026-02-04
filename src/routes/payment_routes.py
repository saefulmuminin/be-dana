from flask import Blueprint
from src.services.payment_service import PaymentService

payment_bp = Blueprint('payment', __name__, url_prefix='/api/v1/content/payment-channels')
paymentService = PaymentService()

@payment_bp.route('/', methods=['GET'])
def getPayment():
    return paymentService.getPaymentChannels()
