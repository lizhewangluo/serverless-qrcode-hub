import logging
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QSystemTrayIcon,
    QMenu, QMessageBox, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QAction, QClipboard, QPixmap
from .worker import ParseWorker, ClipboardWorker
from .parser import ParseResult

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window"""
    
    # Custom signal for hotkey
    hotkey_triggered = Signal()
    
    def __init__(self):
        super().__init__()
        self.parse_worker = None
        self.clipboard_worker = None
        self.clipboard_enabled = True
        self.init_ui()
        self.init_tray()
        self.init_hotkey()
        self.init_clipboard_monitoring()
    
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("Taokouling Float Tool")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.resize(400, 300)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Input section
        input_layout = QHBoxLayout()
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入淘口令或自动从剪贴板检测...")
        self.input_edit.returnPressed.connect(self.on_parse_clicked)
        input_layout.addWidget(self.input_edit)
        
        self.parse_button = QPushButton("解析")
        self.parse_button.clicked.connect(self.on_parse_clicked)
        self.parse_button.setMinimumWidth(60)
        input_layout.addWidget(self.parse_button)
        
        layout.addLayout(input_layout)
        
        # Settings section
        settings_frame = QFrame()
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clipboard_checkbox = QCheckBox("自动检测剪贴板")
        self.clipboard_checkbox.setChecked(True)
        self.clipboard_checkbox.toggled.connect(self.on_clipboard_toggled)
        settings_layout.addWidget(self.clipboard_checkbox)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # Results section
        results_label = QLabel("解析结果:")
        layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        layout.addWidget(self.results_text)
        
        # Status bar
        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)
        
        # Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-family: monospace;
                font-size: 11px;
            }
            QLabel {
                color: #333;
                font-size: 12px;
            }
            QCheckBox {
                font-size: 11px;
                color: #666;
            }
        """)
    
    def init_tray(self):
        """Initialize system tray"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available")
            return
        
        # Create tray icon (using a simple colored pixmap as fallback)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        tray_icon = QIcon(pixmap)
        
        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("Taokouling Float Tool")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏", self)
        hide_action.triggered.connect(self.hide_window)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def init_hotkey(self):
        """Initialize global hotkey"""
        try:
            import keyboard
            
            # Register global hotkey Ctrl+Alt+T
            keyboard.add_hotkey('ctrl+alt+t', self.on_global_hotkey)
            logger.info("Global hotkey Ctrl+Alt+T registered successfully")
            
        except ImportError:
            logger.warning("keyboard module not available, hotkey disabled")
        except Exception as e:
            logger.warning(f"Failed to register global hotkey: {str(e)}")
            self.show_hotkey_help()
    
    def init_clipboard_monitoring(self):
        """Initialize clipboard monitoring"""
        self.clipboard_worker = ClipboardWorker()
        self.clipboard_worker.code_detected.connect(self.on_codes_detected)
        self.clipboard_worker.error_occurred.connect(self.on_clipboard_error)
        self.clipboard_worker.start()
    
    def on_parse_clicked(self):
        """Handle parse button click"""
        text = self.input_edit.text().strip()
        if not text:
            self.show_error("请输入淘口令")
            return
        
        # Extract codes from input
        from .parser import TaokoulingParser
        parser = TaokoulingParser()
        codes = parser.extract_codes(text)
        
        if not codes:
            self.show_error("未检测到有效的淘口令格式")
            return
        
        # Start parsing
        self.start_parsing(codes)
    
    def start_parsing(self, codes):
        """Start parsing codes in background"""
        if self.parse_worker and self.parse_worker.isRunning():
            self.parse_worker.stop()
        
        self.parse_worker = ParseWorker()
        self.parse_worker.set_codes(codes)
        self.parse_worker.result_ready.connect(self.on_parse_result)
        self.parse_worker.error_occurred.connect(self.on_parse_error)
        self.parse_worker.progress_updated.connect(self.on_parse_progress)
        self.parse_worker.finished.connect(self.on_parsing_finished)
        
        self.parse_button.setEnabled(False)
        self.parse_button.setText("解析中...")
        self.status_label.setText(f"正在解析 {len(codes)} 个淘口令...")
        
        self.parse_worker.start()
    
    def on_parse_result(self, result: ParseResult):
        """Handle successful parse result"""
        self.results_text.append(str(result))
        self.results_text.append("-" * 40)
    
    def on_parse_error(self, error_type: str, message: str):
        """Handle parse error"""
        error_msg = self.get_user_friendly_error(error_type, message)
        self.results_text.append(f"❌ {error_msg}")
        self.results_text.append("-" * 40)
    
    def on_parse_progress(self, message: str):
        """Handle parse progress update"""
        self.status_label.setText(message)
    
    def on_parsing_finished(self):
        """Handle parsing finished"""
        self.parse_button.setEnabled(True)
        self.parse_button.setText("解析")
        self.status_label.setText("就绪")
    
    def on_codes_detected(self, codes):
        """Handle detected codes from clipboard"""
        if not self.clipboard_enabled:
            return
        
        # Auto-fill input with detected codes
        if codes:
            self.input_edit.setText(codes[0])
            if len(codes) > 1:
                self.status_label.setText(f"检测到 {len(codes)} 个淘口令")
            
            # Auto-parse if enabled
            if self.clipboard_enabled and self.isVisible():
                self.start_parsing(codes)
    
    def on_clipboard_error(self, error_message: str):
        """Handle clipboard monitoring error"""
        logger.warning(f"Clipboard error: {error_message}")
        self.status_label.setText("剪贴板监控出错")
    
    def on_clipboard_toggled(self, checked: bool):
        """Handle clipboard checkbox toggle"""
        self.clipboard_enabled = checked
        if checked and self.clipboard_worker:
            self.clipboard_worker.reset()
        status = "已启用" if checked else "已禁用"
        self.status_label.setText(f"剪贴板自动检测{status}")
    
    def on_global_hotkey(self):
        """Handle global hotkey press"""
        logger.info("Global hotkey triggered")
        self.hotkey_triggered.emit()
        
        # Show window and trigger parse
        self.show_window()
        if self.input_edit.text().strip():
            self.on_parse_clicked()
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show and bring window to front"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def hide_window(self):
        """Hide window"""
        self.hide()
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.warning(self, "错误", message)
    
    def show_hotkey_help(self):
        """Show hotkey help message"""
        help_msg = (
            "无法注册全局热键 Ctrl+Alt+T\n\n"
            "可能的原因：\n"
            "1. 权限不足\n"
            "2. 其他程序占用了该热键\n"
            "3. 系统不支持全局热键\n\n"
            "您仍可以手动使用程序，只是无法使用热键功能。"
        )
        QMessageBox.information(self, "热键不可用", help_msg)
    
    def get_user_friendly_error(self, error_type: str, message: str) -> str:
        """Get user-friendly error message"""
        error_messages = {
            "invalid_input": "输入格式错误",
            "expired_token": "认证已过期，请检查配置",
            "no_permission": "没有权限访问",
            "rate_limited": "请求过于频繁，请稍后再试",
            "network_error": "网络连接错误",
            "provider_error": "服务提供商错误"
        }
        
        return error_messages.get(error_type, message)
    
    def quit_application(self):
        """Quit the application"""
        if self.parse_worker and self.parse_worker.isRunning():
            self.parse_worker.stop()
        
        if self.clipboard_worker and self.clipboard_worker.isRunning():
            self.clipboard_worker.stop()
        
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle close event - minimize to tray instead of closing"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.status_label.setText("已最小化到系统托盘")
        else:
            self.quit_application()

class TaokoulingApp(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Taokouling Float Tool")
        self.setApplicationVersion("1.0.0")
        self.setQuitOnLastWindowClosed(False)
        
        # Setup logging
        self.setup_logging()
        
        # Create main window
        self.main_window = MainWindow()
        self.main_window.show()
    
    def setup_logging(self):
        """Setup logging configuration"""
        import os
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            log_dir = os.path.join(appdata, 'tkl-float', 'logs')
        else:
            log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5),
                logging.StreamHandler()
            ]
        )
        
        # Redact secrets in logs
        logging.getLogger().addFilter(SecretRedactionFilter())

class SecretRedactionFilter(logging.Filter):
    """Filter to redact secrets in log messages"""
    
    SENSITIVE_PATTERNS = [
        'app_key', 'app_secret', 'invite_code', 'token', 'password'
    ]
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in msg.lower():
                    # Redact sensitive information
                    import re
                    msg = re.sub(rf'{pattern}[=:]\s*[^\s,}]+', f'{pattern}=***', msg, flags=re.IGNORECASE)
                    record.msg = msg
        return True