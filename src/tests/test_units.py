import unittest
from unittest.mock import MagicMock, patch
from src.models.user_model import UserModel
from src.services.auth_service import AuthService

class TestUserModel(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.patcher = patch('src.models.base_model.db', self.mock_db)
        self.patcher.start()
        self.user_model = UserModel()

    def tearDown(self):
        self.patcher.stop()

    def test_create_user(self):
        # Mock DB cursor
        cursor = self.mock_db.getConnection().cursor.return_value.__enter__.return_value
        cursor.lastrowid = 1
        
        data = {'email': 'test@example.com', 'password': 'pass', 'tipe': 'user'}
        user_id = self.user_model.create(data)
        
        self.assertEqual(user_id, 1)
        self.assertTrue(cursor.execute.called)

class TestAuthService(unittest.TestCase):
    @patch('src.models.base_model.db')
    @patch('src.utils.response.jsonify')
    def test_seamless_login(self, mock_jsonify, mock_db):
        # Mock DB connection and cursor for UserModel interactions
        mock_cursor = MagicMock()
        mock_db.get_connection.return_value.cursor.return_value.__enter__.return_value = mock_cursor
        
        # When UserModel queries for user, return a dummy user
        mock_cursor.fetchone.return_value = {'id': 1, 'email': 'test@example.com', 'tipe': 'user'}
        
        mock_jsonify.side_effect = lambda x: x
        
        service = AuthService()
        response, code = service.seamlessLogin('auth_code_123')
        
        self.assertEqual(code, 200)
        self.assertIn('token', response['data'])

if __name__ == '__main__':
    unittest.main()
