import unittest
from unittest.mock import MagicMock, patch

# Patch before importing anything that initializes models
patch('pymysql.connect').start()

from src.services.dana_payment_service import DanaPaymentService
from src.index import app

class TestDanaPaymentService(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Patch Database connection in models
        self.patch_db = patch('src.utils.database.db.getConnection')
        self.mock_db_conn = self.patch_db.start()
        
        # Setup mock connection to return a mock cursor
        self.mock_cursor = MagicMock()
        self.mock_cursor.rowcount = 1
        self.mock_cursor.lastrowid = 1
        self.mock_db_conn.return_value.cursor.return_value.__enter__.return_value = self.mock_cursor
        
        self.service = DanaPaymentService()

    def tearDown(self):
        self.patch_db.stop()
        self.app_context.pop()

    def test_generate_signature(self):
        params = {
            "timestamp": "2025-01-27T10:30:00Z",
            "method": "POST",
            "path": "/test",
            "body": '{"key":"val"}'
        }
        signature = self.service.generateSignature(params)
        self.assertEqual(len(signature), 64)

    @patch('src.services.dana_payment_service.requests.post')
    def test_create_order(self, mock_post):
        # Setup instance mocks
        self.service.paymentModel.findById = MagicMock(return_value={"id": 2, "biaya_admin": 2500, "payment_type": "va"})
        self.service.donationModel.create = MagicMock(return_value=1)
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"responseCode": "2005400", "referenceNo": "REF123", "webRedirectUrl": "http://dana"}
        mock_post.return_value = mock_resp
        
        data = {
            "access_token": "token123",
            "nominal": 100000,
            "email": "test@user.com",
            "metode_id": 2
        }
        response = self.service.createOrder(data)
        with app.app_context():
            print(f"DEBUG RESPONSE STATUS: {response[1]}")
            if response[1] != 200:
                print(f"DEBUG RESPONSE BODY: {response[0].get_json()}")
        self.assertEqual(response[1], 200)

if __name__ == '__main__':
    unittest.main()
