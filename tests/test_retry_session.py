import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import requests
from urllib3.util.retry import Retry

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import get_retry_session

class TestRetrySession(unittest.TestCase):
    
    @patch('app.main.requests.Session')
    def test_get_retry_session_configuration(self, mock_session_class):
        # Setup
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Execute
        session = get_retry_session()
        
        # Verify
        mock_session_class.assert_called_once()
        
        # Verify that mount was called twice (for http and https)
        self.assertEqual(mock_session.mount.call_count, 2)
        
        # Get the retry configuration from the first call to mount
        adapter = mock_session.mount.call_args_list[0][0][1]
        retry = adapter.max_retries
        
        # Verify retry configuration
        self.assertEqual(retry.total, 3)
        self.assertEqual(retry.backoff_factor, 2)
        self.assertEqual(retry.status_forcelist, [500, 502, 503, 504])
    
    def test_get_retry_session_integration(self):
        # This is a more integrated test that doesn't mock the Session class
        session = get_retry_session()
        
        # Verify that the session is a requests.Session
        self.assertIsInstance(session, requests.Session)
        
        # Verify that the session has adapters for http and https
        self.assertTrue(session.adapters.get('http://'))
        self.assertTrue(session.adapters.get('https://'))
        
        # Verify retry configuration
        http_adapter = session.adapters.get('http://')
        retry = http_adapter.max_retries
        
        self.assertEqual(retry.total, 3)
        self.assertEqual(retry.backoff_factor, 2)
        self.assertEqual(retry.status_forcelist, [500, 502, 503, 504])

if __name__ == '__main__':
    unittest.main()
