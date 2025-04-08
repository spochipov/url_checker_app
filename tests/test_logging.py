import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import logging
import tempfile
import shutil

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test the logging configuration
import app.main

class TestLogging(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for logs
        self.test_dir = tempfile.mkdtemp()
        self.original_log_dir = app.main.log_dir
        app.main.log_dir = self.test_dir
        
        # Reset the logger
        app.main.logger.handlers = []
    
    def tearDown(self):
        # Restore the original log directory
        app.main.log_dir = self.original_log_dir
        
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)
    
    @patch('app.main.logging.getLogger')
    @patch('app.main.RotatingFileHandler')
    @patch('app.main.logging.StreamHandler')
    def test_logger_configuration(self, mock_stream_handler, mock_file_handler, mock_get_logger):
        # Setup
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance
        
        mock_stream_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_stream_handler_instance
        
        # Re-import the module to trigger the logging configuration
        import importlib
        importlib.reload(app.main)
        
        # Verify
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_file_handler.assert_called_once()
        mock_stream_handler.assert_called_once()
        mock_logger.addHandler.assert_any_call(mock_file_handler_instance)
        mock_logger.addHandler.assert_any_call(mock_stream_handler_instance)
    
    def test_log_directory_creation(self):
        # Remove the test directory to test creation
        shutil.rmtree(self.test_dir)
        
        # Re-import the module to trigger the log directory creation
        import importlib
        importlib.reload(app.main)
        
        # Verify that the directory was created
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_log_file_creation(self):
        # Re-import the module to trigger the logging configuration
        import importlib
        importlib.reload(app.main)
        
        # Get the log file path
        log_file_path = os.path.join(self.test_dir, "app.log")
        
        # Write a log message
        app.main.logger.info("Test log message")
        
        # Verify that the log file was created
        self.assertTrue(os.path.exists(log_file_path))
        
        # Verify that the log message was written
        with open(log_file_path, 'r') as f:
            log_content = f.read()
            self.assertIn("Test log message", log_content)

if __name__ == '__main__':
    unittest.main()
