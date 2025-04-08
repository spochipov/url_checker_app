import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import logging

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import send_telegram_alert

class TestTelegramAlert(unittest.TestCase):
    
    @patch('app.main.requests.post')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_send_telegram_alert_success(self, mock_logger, mock_getenv, mock_post):
        # Setup
        mock_getenv.side_effect = lambda key: {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': 'test_chat_id'}[key]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Execute
        send_telegram_alert("Test message")
        
        # Verify
        mock_post.assert_called_once_with(
            'https://api.telegram.org/bottest_token/sendMessage',
            json={'chat_id': 'test_chat_id', 'text': 'Test message'},
            timeout=10
        )
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()
    
    @patch('app.main.requests.post')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_send_telegram_alert_missing_credentials(self, mock_logger, mock_getenv, mock_post):
        # Setup - missing token
        mock_getenv.side_effect = lambda key: {'TELEGRAM_BOT_TOKEN': None, 'TELEGRAM_CHAT_ID': 'test_chat_id'}[key]
        
        # Execute
        send_telegram_alert("Test message")
        
        # Verify
        mock_post.assert_not_called()
        mock_logger.warning.assert_called_once()
        
        # Reset mocks
        mock_logger.reset_mock()
        mock_post.reset_mock()
        
        # Setup - missing chat_id
        mock_getenv.side_effect = lambda key: {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': None}[key]
        
        # Execute
        send_telegram_alert("Test message")
        
        # Verify
        mock_post.assert_not_called()
        mock_logger.warning.assert_called_once()
    
    @patch('app.main.requests.post')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_send_telegram_alert_api_error(self, mock_logger, mock_getenv, mock_post):
        # Setup
        mock_getenv.side_effect = lambda key: {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': 'test_chat_id'}[key]
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        # Execute
        send_telegram_alert("Test message")
        
        # Verify
        mock_post.assert_called_once()
        mock_logger.warning.assert_called_once()
    
    @patch('app.main.requests.post')
    @patch('app.main.os.getenv')
    @patch('app.main.logger')
    def test_send_telegram_alert_exception(self, mock_logger, mock_getenv, mock_post):
        # Setup
        mock_getenv.side_effect = lambda key: {'TELEGRAM_BOT_TOKEN': 'test_token', 'TELEGRAM_CHAT_ID': 'test_chat_id'}[key]
        mock_post.side_effect = Exception("Test exception")
        
        # Execute
        send_telegram_alert("Test message")
        
        # Verify
        mock_post.assert_called_once()
        mock_logger.error.assert_called_once()

if __name__ == '__main__':
    unittest.main()
