import unittest
from unittest.mock import MagicMock, patch
from src.services.simba_service import SimbaService

class TestSimbaService(unittest.TestCase):
    
    @patch('requests.post')
    def test_register_muzaki(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'status_code': '000', 'npwz': '123456789'}
        mock_post.return_value = mock_response
        
        service = SimbaService()
        npwz = service.registerMuzaki(
            {'nama_lengkap': 'Fulan', 'email': 'fulan@example.com'},
            {'kode_institusi': 'PST', 'apikey': 'key', 'email': 'amil@baznas.go.id'}
        )
        self.assertEqual(npwz, '123456789')

    @patch('requests.post')
    def test_save_transaction(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'status_code': '000', 'no_transaksi': 'TRX123'}
        mock_post.return_value = mock_response
        
        service = SimbaService()
        result = service.saveTransaction(
            {'id': 1, 'npwz': '123', 'nominal': 10000},
            {'name': 'Campaign 1', 'tipe': 'zakat'},
            {'kode_institusi': 'PST', 'apikey': 'key', 'email': 'amil@baznas.go.id'},
            {'code': '123'}
        )
        self.assertIsNotNone(result)
        self.assertEqual(result['no_transaksi'], 'TRX123')

if __name__ == '__main__':
    unittest.main()
