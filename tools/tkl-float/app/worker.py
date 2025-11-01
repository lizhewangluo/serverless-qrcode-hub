import logging
from PySide6.QtCore import QThread, Signal
from typing import List, Optional, Dict
from ..parser import TaokoulingParser, ParseResult, ParseError
from ..providers.lottefuture import LotteFutureProvider

logger = logging.getLogger(__name__)

class ParseWorker(QThread):
    """Worker thread for parsing taokouling codes"""
    
    # Signals
    result_ready = Signal(object)  # ParseResult
    error_occurred = Signal(str, str)  # error_type, message
    progress_updated = Signal(str)  # status message
    finished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.codes = []
        self.parser = TaokoulingParser()
        self.provider = LotteFutureProvider()
        self._running = False
    
    def set_codes(self, codes: List[str]):
        """Set codes to parse"""
        self.codes = codes
    
    def run(self):
        """Execute parsing in background thread"""
        self._running = True
        
        if not self.codes:
            self.error_occurred.emit("invalid_input", "No codes to parse")
            self.finished.emit()
            return
        
        logger.info(f"Starting to parse {len(self.codes)} codes")
        
        for i, code in enumerate(self.codes):
            if not self._running:
                break
            
            try:
                # Normalize code
                normalized_code = self.parser.normalize_code(code)
                
                # Update progress
                self.progress_updated.emit(f"Parsing code {i+1}/{len(self.codes)}: {normalized_code[:8]}...")
                
                # Parse using provider
                result = self.provider.parse(normalized_code)
                
                # Emit result
                self.result_ready.emit(result)
                
                logger.info(f"Successfully parsed code {i+1}/{len(self.codes)}")
                
            except ParseError as e:
                logger.warning(f"Parse error for code {code[:8]}...: {e.message}")
                self.error_occurred.emit(e.error_type, e.message)
            except Exception as e:
                logger.exception(f"Unexpected error parsing code {code[:8]}...: {str(e)}")
                self.error_occurred.emit("provider_error", f"Unexpected error: {str(e)}")
        
        self.finished.emit()
    
    def stop(self):
        """Stop the worker thread"""
        self._running = False
        self.wait()
    
    def __del__(self):
        """Cleanup"""
        self.stop()

class ClipboardWorker(QThread):
    """Worker thread for monitoring clipboard"""
    
    # Signals
    code_detected = Signal(list)  # List of detected codes
    error_occurred = Signal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parser = TaokoulingParser()
        self._running = False
        self._last_clipboard = ""
    
    def run(self):
        """Monitor clipboard for taokouling codes"""
        self._running = True
        
        try:
            from PySide6.QtGui import QClipboard
            from PySide6.QtWidgets import QApplication
            
            clipboard = QApplication.clipboard()
            
            while self._running:
                try:
                    # Get current clipboard text
                    current_text = clipboard.text()
                    
                    # Check if clipboard changed and contains taokouling codes
                    if current_text != self._last_clipboard:
                        codes = self.parser.extract_codes(current_text)
                        
                        if codes:
                            logger.info(f"Detected {len(codes)} taokouling codes in clipboard")
                            self.code_detected.emit(codes)
                        
                        self._last_clipboard = current_text
                    
                    # Sleep for a short interval to avoid high CPU usage
                    self.msleep(500)
                    
                except Exception as e:
                    logger.warning(f"Error monitoring clipboard: {str(e)}")
                    self.error_occurred.emit(f"Clipboard error: {str(e)}")
                    self.msleep(1000)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"Failed to start clipboard monitoring: {str(e)}")
            self.error_occurred.emit(f"Clipboard monitoring failed: {str(e)}")
    
    def stop(self):
        """Stop the clipboard monitoring"""
        self._running = False
        self.wait()
    
    def reset(self):
        """Reset the last clipboard state"""
        self._last_clipboard = ""
    
    def __del__(self):
        """Cleanup"""
        self.stop()