import re
import logging
from typing import Dict, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ParseError(Exception):
    """Base exception for parsing errors"""
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)

class InvalidInputError(ParseError):
    def __init__(self, message: str = "Invalid taokouling format"):
        super().__init__("invalid_input", message)

class ExpiredTokenError(ParseError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__("expired_token", message)

class NoPermissionError(ParseError):
    def __init__(self, message: str = "No permission to access this resource"):
        super().__init__("no_permission", message)

class RateLimitedError(ParseError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__("rate_limited", message)

class NetworkError(ParseError):
    def __init__(self, message: str = "Network error occurred"):
        super().__init__("network_error", message)

class ProviderError(ParseError):
    def __init__(self, message: str = "Provider error occurred"):
        super().__init__("provider_error", message)

class TaokoulingParser:
    """Parser for extracting taokouling codes"""
    
    # Strict regex patterns for taokouling formats
    PATTERNS = [
        r'￥([^￥]+)￥',  # ￥xxx￥ format
        r'€([^€]+)€',    # €xxx€ format  
        r'₤([^₤]+)₤',    # ₤xxx₤ format
        r'ɂ([^ɂ]+)ɂ',    # ɂxxxɂ format
        r'9/([^/]+)/',   # 9/xxx/ format
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern) for pattern in self.PATTERNS]
    
    def extract_codes(self, text: str) -> list[str]:
        """Extract all taokouling codes from text"""
        if not text:
            return []
        
        codes = []
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            codes.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_codes = []
        for code in codes:
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        
        logger.debug(f"Extracted {len(unique_codes)} codes from text")
        return unique_codes
    
    def normalize_code(self, code: str) -> str:
        """Normalize and validate a taokouling code"""
        if not code:
            raise InvalidInputError("Empty code")
        
        # Remove whitespace
        code = code.strip()
        
        # Basic validation - should be alphanumeric with some allowed chars
        if not re.match(r'^[a-zA-Z0-9\-_]+$', code):
            raise InvalidInputError(f"Invalid code format: {code}")
        
        return code

class Provider(ABC):
    """Abstract base class for taokouling providers"""
    
    @abstractmethod
    def parse(self, code: str) -> Dict[str, str]:
        """Parse a taokouling code and return item information"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name"""
        pass

class ParseResult:
    """Result of parsing a taokouling code"""
    
    def __init__(self, item_id: str, item_url: str, title: str, provider: str):
        self.item_id = item_id
        self.item_url = item_url
        self.title = title
        self.provider = provider
    
    def to_dict(self) -> Dict[str, str]:
        return {
            'item_id': self.item_id,
            'item_url': self.item_url,
            'title': self.title,
            'provider': self.provider
        }
    
    def __str__(self) -> str:
        return f"[{self.provider}] {self.title}\nID: {self.item_id}\nURL: {self.item_url}"