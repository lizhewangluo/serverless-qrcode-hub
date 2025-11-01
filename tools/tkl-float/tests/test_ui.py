import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui import MainWindow

class TestUISmoke(unittest.TestCase):
    """UI smoke test - launch and close application"""
    
    @classmethod
    def setUpClass(cls):
        """Create QApplication for testing"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test case"""
        self.window = MainWindow()
    
    def tearDown(self):
        """Clean up after test"""
        self.window.close()
    
    def test_window_creation(self):
        """Test window can be created"""
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "Taokouling Float Tool")
    
    def test_window_attributes(self):
        """Test window has correct attributes"""
        # Check if window has required widgets
        self.assertIsNotNone(self.window.input_edit)
        self.assertIsNotNone(self.window.parse_button)
        self.assertIsNotNone(self.window.results_text)
        self.assertIsNotNone(self.window.clipboard_checkbox)
        self.assertIsNotNone(self.window.status_label)
    
    def test_parse_button_initial_state(self):
        """Test parse button initial state"""
        self.assertTrue(self.window.parse_button.isEnabled())
        self.assertEqual(self.window.parse_button.text(), "解析")
    
    def test_clipboard_checkbox_initial_state(self):
        """Test clipboard checkbox initial state"""
        self.assertTrue(self.window.clipboard_checkbox.isChecked())
    
    def test_status_label_initial_state(self):
        """Test status label initial state"""
        self.assertEqual(self.window.status_label.text(), "就绪")
    
    def test_input_placeholder(self):
        """Test input field placeholder"""
        placeholder = self.window.input_edit.placeholderText()
        self.assertIn("输入淘口令", placeholder)
        self.assertIn("剪贴板", placeholder)
    
    def test_window_is_top_hint(self):
        """Test window has stay-on-top hint"""
        from PySide6.QtCore import Qt
        window_flags = self.window.windowFlags()
        self.assertTrue(window_flags & Qt.WindowType.WindowStaysOnTopHint)
    
    def test_parse_with_empty_input(self):
        """Test parse with empty input shows error"""
        with patch.object(self.window, 'show_error') as mock_show_error:
            self.window.input_edit.setText("")
            self.window.on_parse_clicked()
            mock_show_error.assert_called_once_with("请输入淘口令")
    
    def test_parse_with_invalid_format(self):
        """Test parse with invalid format shows error"""
        with patch.object(self.window, 'show_error') as mock_show_error:
            self.window.input_edit.setText("invalid format")
            self.window.on_parse_clicked()
            mock_show_error.assert_called_once_with("未检测到有效的淘口令格式")
    
    def test_parse_with_valid_format(self):
        """Test parse with valid format starts parsing"""
        with patch.object(self.window, 'start_parsing') as mock_start:
            self.window.input_edit.setText("￥ABC123￥")
            self.window.on_parse_clicked()
            mock_start.assert_called_once_with(['ABC123'])
    
    def test_clipboard_toggle(self):
        """Test clipboard checkbox toggle"""
        # Initially enabled
        self.assertTrue(self.window.clipboard_enabled)
        
        # Disable
        self.window.clipboard_checkbox.setChecked(False)
        self.assertFalse(self.window.clipboard_enabled)
        
        # Enable
        self.window.clipboard_checkbox.setChecked(True)
        self.assertTrue(self.window.clipboard_enabled)
    
    def test_user_friendly_error_messages(self):
        """Test user-friendly error message mapping"""
        test_cases = [
            ("invalid_input", "输入格式错误"),
            ("expired_token", "认证已过期，请检查配置"),
            ("no_permission", "没有权限访问"),
            ("rate_limited", "请求过于频繁，请稍后再试"),
            ("network_error", "网络连接错误"),
            ("provider_error", "服务提供商错误"),
            ("unknown_error", "unknown_error")  # Should return original message
        ]
        
        for error_type, expected in test_cases:
            result = self.window.get_user_friendly_error(error_type, "original message")
            self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()