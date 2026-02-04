import unittest
from unittest.mock import MagicMock, patch

# Patch before importing anything that initializes models
patch('pymysql.connect').start()

from src.services.health_service import HealthService

class TestHealthService(unittest.TestCase):
    def setUp(self):
        self.service = HealthService()

    @patch('src.utils.database.db.getConnection')
    def test_check_database_success(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = self.service.checkDatabase()
        self.assertTrue(result)
        mock_conn.close.assert_called_once()

    @patch('src.utils.database.db.getConnection')
    def test_check_database_failure(self, mock_get_conn):
        mock_get_conn.side_effect = Exception("DB Error")
        
        result = self.service.checkDatabase()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
