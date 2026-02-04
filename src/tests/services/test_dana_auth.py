import unittest
from unittest.mock import MagicMock, patch

# Patch before importing anything that initializes models
patch('pymysql.connect').start()

from src.services.dana_auth_service import DanaAuthService
from src.index import app

class TestDanaAuthService(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.service = DanaAuthService()

    def tearDown(self):
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

    def test_get_headers(self):
        headers = self.service.getHeaders("ts", "sig")
        self.assertEqual(headers["X-SIGNATURE"], "sig")
        self.assertEqual(headers["X-TIMESTAMP"], "ts")

    def test_generate_oauth_url(self):
        data = {"redirect_url": "http://test.com"}
        response = self.service.generateOauthUrl(data)
        self.assertEqual(response[1], 200)

if __name__ == '__main__':
    unittest.main()
