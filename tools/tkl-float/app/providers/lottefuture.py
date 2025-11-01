import requests
import logging
from typing import Dict
from urllib.parse import urljoin
from ..parser import Provider, ParseResult, NetworkError, ProviderError, ExpiredTokenError, NoPermissionError, RateLimitedError
from ..settings import settings

logger = logging.getLogger(__name__)

class LotteFutureProvider(Provider):
    """LotteFuture API provider for taokouling parsing"""
    
    def __init__(self):
        self.base_url = settings.base_url
        self.app_key = settings.app_key
        self.app_secret = settings.app_secret
        self.invite_code = settings.invite_code
        self.timeout = settings.timeout
        
        # Create session with retry configuration
        self.session = requests.Session()
        
        # Configure retries with exponential backoff
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_name(self) -> str:
        return "LotteFuture"
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make HTTP request with proper error handling"""
        if not all([self.base_url, self.app_key, self.app_secret, self.invite_code]):
            raise ProviderError("Missing required configuration")
        
        url = urljoin(self.base_url, endpoint)
        
        # Default parameters
        request_params = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'invite_code': self.invite_code,
        }
        
        if params:
            request_params.update(params)
        
        try:
            logger.debug(f"Making request to {url}")
            response = self.session.get(
                url,
                params=request_params,
                timeout=(self.timeout // 2, self.timeout)  # Connect/Read timeout split
            )
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"Response status: {data.get('code', 'unknown')}")
            
            return data
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timeout after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Connection failed")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ExpiredTokenError("Authentication failed - check credentials")
            elif e.response.status_code == 403:
                raise NoPermissionError("Access forbidden")
            elif e.response.status_code == 429:
                raise RateLimitedError("Rate limit exceeded")
            else:
                raise NetworkError(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise ProviderError(f"Invalid JSON response: {str(e)}")
    
    def parse(self, code: str) -> ParseResult:
        """Parse a taokouling code using LotteFuture API"""
        try:
            # Make API request
            response = self._make_request('/api/parse', {'code': code})
            
            # Check response code
            if response.get('code') != 0:
                error_msg = response.get('message', 'Unknown error')
                
                # Map error codes to our exceptions
                error_code = response.get('code')
                if error_code == 401:
                    raise ExpiredTokenError(error_msg)
                elif error_code == 403:
                    raise NoPermissionError(error_msg)
                elif error_code == 429:
                    raise RateLimitedError(error_msg)
                else:
                    raise ProviderError(f"API error {error_code}: {error_msg}")
            
            # Extract data
            data = response.get('data', {})
            item_id = data.get('item_id', '')
            item_url = data.get('item_url', '')
            title = data.get('title', '')
            
            if not all([item_id, item_url, title]):
                raise ProviderError("Incomplete response data from provider")
            
            logger.info(f"Successfully parsed code {code[:8]}...")
            return ParseResult(item_id, item_url, title, self.get_name())
            
        except (NetworkError, ProviderError, ExpiredTokenError, NoPermissionError, RateLimitedError):
            raise
        except Exception as e:
            logger.exception(f"Unexpected error parsing code: {str(e)}")
            raise ProviderError(f"Unexpected error: {str(e)}")
    
    def __del__(self):
        """Cleanup session"""
        if hasattr(self, 'session'):
            self.session.close()