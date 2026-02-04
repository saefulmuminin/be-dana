from src.models.payment_model import PaymentModel
from src.utils.response import Response

class PaymentService:
    def __init__(self):
        self.model = PaymentModel()

    def getPaymentChannels(self):
        data = self.model.getGroupedPayments()
        return Response.success(data)
