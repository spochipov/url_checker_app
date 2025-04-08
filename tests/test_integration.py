import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import requests
import logging

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import send_telegram_alert, get_retry_session

class TestIntegration(unittest.TestCase):
    
    @patch('app.main.requests.post')
    def test_telegram_alert_integration(self, mock_post):
        # Setup
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
        os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Execute
        send_telegram_alert("Test integration message")
        
        # Verify
        mock_post.assert_called_once_with(
            'https://api.telegram.org/bottest_token/sendMessage',
            json={'chat_id': 'test_chat_id', 'text': 'Test integration message'},
            timeout=10
        )
        
        # Cleanup
        del os.environ['TELEGRAM_BOT_TOKEN']
        del os.environ['TELEGRAM_CHAT_ID']
    
    def test_retry_session_with_mock_server(self):
        # This test would ideally use a mock server to test the retry functionality
        # For simplicity, we'll just verify that the session is configured correctly
        session = get_retry_session()
        
        # Verify session configuration
        adapter = session.adapters['https://']
        retry = adapter.max_retries
        
        self.assertEqual(retry.total, 3)
        self.assertEqual(retry.backoff_factor, 2)
        self.assertEqual(retry.status_forcelist, [500, 502, 503, 504])
        
        # In a real integration test, we would set up a mock server that returns
        # 503 errors a few times and then succeeds, and verify that the client
        # successfully retries and eventually gets the response.

if __name__ == '__main__':
    unittest.main()
