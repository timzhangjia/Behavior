"""
Configuration Settings Module - Manages framework configuration parameters
"""

import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ViewportConfig:
    """Viewport configuration"""
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height


class BrowserConfig:
    """Browser configuration"""
    def __init__(self, headless: bool = False, browser_type: str = "chromium", 
                 browser_args: List[str] = None, user_agent: Optional[str] = None,
                 locale: str = "zh-CN", timezone: str = "Asia/Shanghai"):
        self.headless = headless
        self.browser_type = browser_type
        self.browser_args = browser_args or []
        self.user_agent = user_agent
        self.locale = locale
        self.timezone = timezone


class TimeoutConfig:
    """Timeout configuration"""
    def __init__(self, default_timeout: int = 30000, navigation_timeout: int = 30000,
                 action_timeout: int = 30000):
        self.default_timeout = default_timeout
        self.navigation_timeout = navigation_timeout
        self.action_timeout = action_timeout


class LoggingConfig:
    """Logging configuration"""
    def __init__(self, level: str = "INFO", format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
                 file_path: Optional[str] = None, max_file_size: str = "10 MB",
                 backup_count: int = 5):
        self.level = level
        self.format = format
        self.file_path = file_path
        self.max_file_size = max_file_size
        self.backup_count = backup_count


class ScreenshotConfig:
    """Screenshot configuration"""
    def __init__(self, on_failure: bool = True, on_success: bool = False,
                 directory: str = "screenshots", full_page: bool = False):
        self.on_failure = on_failure
        self.on_success = on_success
        self.directory = directory
        self.full_page = full_page


class Settings:
    """Main configuration class"""
    def __init__(self):
        self.viewport = ViewportConfig()
        self.browser = BrowserConfig()
        self.timeout = TimeoutConfig()
        self.logging = LoggingConfig()
        self.screenshot = ScreenshotConfig()
        
        # Configuration read from environment variables
        self.base_url = os.getenv("BASE_URL", "")
        self.api_base_url = os.getenv("API_BASE_URL", "")
        self.test_data_dir = os.getenv("TEST_DATA_DIR", "test_data")
        self.reports_dir = os.getenv("REPORTS_DIR", "reports")
        self.api_data_dir = os.getenv("API_DATA_DIR", "data/api")
        
        # Load environment variable configuration
        self.load_from_env()
    
    # Compatibility properties
    @property
    def headless(self) -> bool:
        return self.browser.headless
    
    @property
    def browser_args(self) -> List[str]:
        return self.browser.browser_args
    
    @property
    def user_agent(self) -> Optional[str]:
        return self.browser.user_agent
    
    @property
    def locale(self) -> str:
        return self.browser.locale
    
    @property
    def timezone(self) -> str:
        return self.browser.timezone
    
    @property
    def default_timeout(self) -> int:
        return self.timeout.default_timeout
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables"""
        self.browser.headless = os.getenv("HEADLESS", "false").lower() == "true"
        self.browser.browser_type = os.getenv("BROWSER_TYPE", "chromium")
        self.browser.locale = os.getenv("LOCALE", "zh-CN")
        self.browser.timezone = os.getenv("TIMEZONE", "Asia/Shanghai")
        
        self.timeout.default_timeout = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
        self.timeout.navigation_timeout = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))
        self.timeout.action_timeout = int(os.getenv("ACTION_TIMEOUT", "30000"))
        
        self.logging.level = os.getenv("LOG_LEVEL", "INFO")
        self.logging.file_path = os.getenv("LOG_FILE_PATH")
        
        self.screenshot.on_failure = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
        self.screenshot.on_success = os.getenv("SCREENSHOT_ON_SUCCESS", "false").lower() == "true"
        self.screenshot.directory = os.getenv("SCREENSHOT_DIR", "screenshots")
        
        self.base_url = os.getenv("BASE_URL", "")
        self.api_base_url = os.getenv("API_BASE_URL", "")
        self.test_data_dir = os.getenv("TEST_DATA_DIR", "test_data")
        self.reports_dir = os.getenv("REPORTS_DIR", "reports")
        self.api_data_dir = os.getenv("API_DATA_DIR", "data/api")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {
            "viewport": {"width": self.viewport.width, "height": self.viewport.height},
            "browser": {
                "headless": self.browser.headless,
                "browser_type": self.browser.browser_type,
                "browser_args": self.browser.browser_args,
                "user_agent": self.browser.user_agent,
                "locale": self.browser.locale,
                "timezone": self.browser.timezone
            },
            "timeout": {
                "default_timeout": self.timeout.default_timeout,
                "navigation_timeout": self.timeout.navigation_timeout,
                "action_timeout": self.timeout.action_timeout
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count
            },
            "screenshot": {
                "on_failure": self.screenshot.on_failure,
                "on_success": self.screenshot.on_success,
                "directory": self.screenshot.directory,
                "full_page": self.screenshot.full_page
            },
            "base_url": self.base_url,
            "api_base_url": self.api_base_url,
            "test_data_dir": self.test_data_dir,
            "reports_dir": self.reports_dir,
            "api_data_dir": self.api_data_dir
        }
