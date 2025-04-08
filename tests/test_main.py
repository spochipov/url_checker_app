import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys
import logging

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import main

class TestMain(unittest.TestCase):
    
    @patch('app.main.time.sleep')
    @patch('app.main.send_telegram_alert')
    @patch('app.main.get_retry_session')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_main_success_response(self, mock_logger, mock_getenv, mock_get_session, mock_send_alert, mock_sleep):
        # Setup to break out of the infinite loop after one iteration
        mock_sleep.side_effect = [None, Exception("Break loop")]
        
        # Setup environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'URL_TO_CHECK': 'https://example.com',
            'INTERVAL_SECONDS': '30'
        }.get(key, default)
        
        # Setup mock session
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session
        
        # Execute (will raise the exception we use to break the loop)
        with self.assertRaises(Exception) as context:
            main()
        
        self.assertEqual(str(context.exception), "Break loop")
        
        # Verify
        mock_getenv.assert_any_call('URL_TO_CHECK')
        mock_getenv.assert_any_call('INTERVAL_SECONDS', '60')
        mock_get_session.assert_called_once()
        mock_session.get.assert_called_once_with('https://example.com', timeout=10)
        mock_logger.info.assert_any_call('Начинаем проверку URL: https://example.com каждые 30 секунд')
        mock_logger.info.assert_any_call('Успешный запрос: статус 200 от https://example.com')
        mock_send_alert.assert_not_called()
        mock_sleep.assert_called_once_with(30)
    
    @patch('app.main.time.sleep')
    @patch('app.main.send_telegram_alert')
    @patch('app.main.get_retry_session')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_main_error_response(self, mock_logger, mock_getenv, mock_get_session, mock_send_alert, mock_sleep):
        # Setup to break out of the infinite loop after one iteration
        mock_sleep.side_effect = [None, Exception("Break loop")]
        
        # Setup environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'URL_TO_CHECK': 'https://example.com',
            'INTERVAL_SECONDS': '30'
        }.get(key, default)
        
        # Setup mock session with error response
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session
        
        # Execute (will raise the exception we use to break the loop)
        with self.assertRaises(Exception) as context:
            main()
        
        self.assertEqual(str(context.exception), "Break loop")
        
        # Verify
        mock_session.get.assert_called_once_with('https://example.com', timeout=10)
        mock_logger.error.assert_called_once()
        mock_send_alert.assert_called_once()
        mock_sleep.assert_called_once_with(30)
    
    @patch('app.main.time.sleep')
    @patch('app.main.send_telegram_alert')
    @patch('app.main.get_retry_session')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_main_request_exception(self, mock_logger, mock_getenv, mock_get_session, mock_send_alert, mock_sleep):
        # Setup to break out of the infinite loop after one iteration
        mock_sleep.side_effect = [None, Exception("Break loop")]
        
        # Setup environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'URL_TO_CHECK': 'https://example.com',
            'INTERVAL_SECONDS': '30'
        }.get(key, default)
        
        # Setup mock session with exception
        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("Connection error")
        mock_get_session.return_value = mock_session
        
        # Execute (will raise the exception we use to break the loop)
        with self.assertRaises(Exception) as context:
            main()
        
        self.assertEqual(str(context.exception), "Break loop")
        
        # Verify
        mock_session.get.assert_called_once_with('https://example.com', timeout=10)
        mock_logger.error.assert_called_once()
        mock_send_alert.assert_called_once()
        mock_sleep.assert_called_once_with(30)
    
    @patch('app.main.logger')
    def test_main_missing_url(self, mock_logger):
        # Setup environment variables - missing URL
        with patch('app.main.os.getenv', return_value=None):
            # Execute
            main()
            
            # Verify
            mock_logger.error.assert_called_once_with("Переменная окружения URL_TO_CHECK не задана.")

if __name__ == '__main__':
    unittest.main()
