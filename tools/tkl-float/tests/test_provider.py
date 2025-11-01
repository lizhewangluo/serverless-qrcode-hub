import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from providers.lottefuture import LotteFutureProvider
from parser import NetworkError, ProviderError, ExpiredTokenError, NoPermissionError, RateLimitedError

class TestLotteFutureProvider(unittest.TestCase):
    """Test cases for LotteFutureProvider"""
    
    def setUp(self):
        self.provider = LotteFutureProvider()
    
    def test_get_name(self):
        """Test provider name"""
        self.assertEqual(self.provider.get_name(), "LotteFuture")
    
    @patch('providers.lottefuture.settings')
    def test_missing_configuration(self, mock_settings):
        """Test behavior with missing configuration"""
        mock_settings.base_url = ""
        mock_settings.app_key = ""
        mock_settings.app_secret = ""
        mock_settings.invite_code = ""
        
        with self.assertRaises(ProviderError) as context:
            self.provider.parse("TEST123")
        
        self.assertIn("Missing required configuration", str(context.exception))
    
    @patch('providers.lottefuture.settings')
    @patch('providers.lottefuture.requests.Session.get')
    def test_successful_parse(self, mock_get, mock_settings):
        """Test successful parsing"""
        # Mock settings
        mock_settings.base_url = "https://api.example.com"
        mock_settings.app_key = "test_key"
        mock_settings.app_secret = "test_secret"
        mock_settings.invite_code = "test_invite"
        mock_settings.timeout = 30
        
        # Mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'item_id': 'ITEM123',
                'item_url': 'https://example.com/item/123',
                'title': 'Test Item'
            }
        }
        mock_get.return_value = mock_response
        
        # Test parsing
        result = self.provider.parse("TEST123")
        
        self.assertEqual(result.item_id, "ITEM123")
        self.assertEqual(result.item_url, "https://example.com/item/123")
        self.assertEqual(result.title, "Test Item")
        self.assertEqual(result.provider, "LotteFuture")
    
    @patch('providers.lottefuture.settings')
    @patch('providers.lottefuture.requests.Session.get')
    def test_api_error_response(self, mock_get, mock_settings):
        """Test API error response"""
        # Mock settings
        mock_settings.base_url = "https://api.example.com"
        mock_settings.app_key = "test_key"
        mock_settings.app_secret = "test_secret"
        mock_settings.invite_code = "test_invite"
        mock_settings.timeout = 30
        
        # Mock error response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'code': 401,
            'message': 'Authentication failed'
        }
        mock_get.return_value = mock_response
        
        # Test parsing
        with self.assertRaises(ExpiredTokenError) as context:
            self.provider.parse("TEST123")
        
        self.assertIn("Authentication failed", str(context.exception))
    
    @patch('providers.lottefuture.settings')
    @patch('providers.lottefuture.requests.Session.get')
    def test_network_timeout(self, mock_get, mock_settings):
        """Test network timeout"""
        # Mock settings
        mock_settings.base_url = "https://api.example.com"
        mock_settings.app_key = "test_key"
        mock_settings.app_secret = "test_secret"
        mock_settings.invite_code = "test_invite"
        mock_settings.timeout = 30
        
        # Mock timeout exception
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        # Test parsing
        with self.assertRaises(NetworkError) as context:
            self.provider.parse("TEST123")
        
        self.assertIn("Request timeout", str(context.exception))
    
    @patch('providers.lottefuture.settings')
    @patch('providers.lottefuture.requests.Session.get')
    def test_http_error_403(self, mock_get, mock_settings):
        """Test HTTP 403 error"""
        # Mock settings
        mock_settings.base_url = "https://api.example.com"
        mock_settings.app_key = "test_key"
        mock_settings.app_secret = "test_secret"
        mock_settings.invite_code = "test_invite"
        mock_settings.timeout = 30
        
        # Mock HTTP error
        import requests
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        # Test parsing
        with self.assertRaises(NoPermissionError):
            self.provider.parse("TEST123")
    
    @patch('providers.lottefuture.settings')
    @patch('providers.lottefuture.requests.Session.get')
    def test_incomplete_response_data(self, mock_get, mock_settings):
        """Test incomplete response data"""
        # Mock settings
        mock_settings.base_url = "https://api.example.com"
        mock_settings.app_key = "test_key"
        mock_settings.app_secret = "test_secret"
        mock_settings.invite_code = "test_invite"
        mock_settings.timeout = 30
        
        # Mock incomplete response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'item_id': 'ITEM123',
                'item_url': ''  # Missing title
            }
        }
        mock_get.return_value = mock_response
        
        # Test parsing
        with self.assertRaises(ProviderError) as context:
            self.provider.parse("TEST123")
        
        self.assertIn("Incomplete response data", str(context.exception))

if __name__ == "__main__":
    unittest.main()