import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Settings:
    def __init__(self):
        self.base_url = ""
        self.app_key = ""
        self.app_secret = ""
        self.invite_code = ""
        self.timeout = 30
        self.load_env()
    
    def load_env(self):
        """Load environment variables from %APPDATA%/tkl-float/.env or fallback to .env"""
        env_files = []
        
        # Try APPDATA path first (Windows production)
        if os.name == 'nt':
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                appdata_env = Path(appdata) / 'tkl-float' / '.env'
                if appdata_env.exists():
                    env_files.append(str(appdata_env))
        
        # Fallback to local .env (development)
        local_env = Path(__file__).parent.parent / '.env'
        if local_env.exists():
            env_files.append(str(local_env))
        
        if not env_files:
            logger.warning("No .env file found. Using default values.")
            return
        
        # Load the first available env file
        load_dotenv(env_files[0])
        logger.info(f"Loaded environment from: {env_files[0]}")
        
        # Load settings
        self.base_url = os.getenv('LT_BASE_URL', '').rstrip('/')
        self.app_key = os.getenv('LT_APP_KEY', '')
        self.app_secret = os.getenv('LT_APP_SECRET', '')
        self.invite_code = os.getenv('LT_INVITE_CODE', '')
        self.timeout = int(os.getenv('LT_TIMEOUT', '30'))
        
        # Validate required settings
        missing = [key for key, value in [
            ('LT_BASE_URL', self.base_url),
            ('LT_APP_KEY', self.app_key),
            ('LT_APP_SECRET', self.app_secret),
            ('LT_INVITE_CODE', self.invite_code)
        ] if not value]
        
        if missing:
            logger.warning(f"Missing environment variables: {', '.join(missing)}")
    
    def get_config(self):
        """Get configuration dictionary (with secrets redacted for logging)"""
        return {
            'base_url': self.base_url,
            'app_key': self.app_key[:4] + '***' if self.app_key else '',
            'app_secret': self.app_secret[:4] + '***' if self.app_secret else '',
            'invite_code': self.invite_code[:4] + '***' if self.invite_code else '',
            'timeout': self.timeout
        }

settings = Settings()