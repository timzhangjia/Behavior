"""
API Request Module - HTTP request handling and response management
"""

import json
import aiohttp
from typing import Optional, Dict, Any, Union
from ..config.settings import Settings
from ..utils.logger import Logger


class Response:
    """HTTP Response wrapper class"""
    
    def __init__(self, status: int, headers: Dict[str, str], content: bytes, 
                 text: str, url: str):
        self.status = status
        self.headers = headers
        self.content = content
        self.text = text
        self.url = url
        self.logger = Logger()
        
        # Parse JSON if possible
        self._json_data = None
        try:
            if self.text and self.is_json():
                self._json_data = json.loads(self.text)
        except json.JSONDecodeError:
            pass
    
    def is_json(self) -> bool:
        """Check if response is JSON format"""
        # Check content-type header
        content_type = self.headers.get('content-type', '').lower()
        if 'application/json' in content_type:
            return True
        
        # If no content-type or not explicitly JSON, try to parse as JSON
        if self.text:
            try:
                import json
                json.loads(self.text)
                return True
            except (json.JSONDecodeError, ValueError):
                return False
        
        return False
    
    def json(self) -> Optional[Dict[str, Any]]:
        """Get JSON data from response"""
        return self._json_data
    
    def get_header(self, name: str) -> Optional[str]:
        """Get header value by name (case insensitive)"""
        name_lower = name.lower()
        for header_name, value in self.headers.items():
            if header_name.lower() == name_lower:
                return value
        return None
    
    def get_json_value(self, key: str, default: Any = None) -> Any:
        """Get value from JSON response by key (supports nested keys with dot notation)"""
        if self._json_data is None:
            return default
        
        keys = key.split('.')
        value = self._json_data
        
        try:
            for k in keys:
                if isinstance(value, dict):
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default
    
    def is_success(self) -> bool:
        """Check if response is successful (2xx status)"""
        return 200 <= self.status < 300
    
    def is_client_error(self) -> bool:
        """Check if response is client error (4xx status)"""
        return 400 <= self.status < 500
    
    def is_server_error(self) -> bool:
        """Check if response is server error (5xx status)"""
        return 500 <= self.status < 600
    
    def size(self) -> int:
        """Get response size in bytes"""
        return len(self.content)
    
    def __repr__(self) -> str:
        return f"Response(status={self.status}, url='{self.url}')"


class APIRequest:
    """API Request handler - manages HTTP requests and responses"""
    
    def __init__(self, settings: Optional[Settings] = None, base_url: Optional[str] = None):
        """
        Initialize API request handler
        
        Args:
            settings: Settings instance
            base_url: Base URL for API requests
        """
        self.settings = settings or Settings()
        self.base_url = base_url or self.settings.base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = Logger()
        
        # Default headers
        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Behavior-Framework/1.0.0"
        }
        
        # Default timeout
        self.timeout = aiohttp.ClientTimeout(total=self.settings.timeout.default_timeout / 1000)
    
    async def start(self) -> None:
        """Start HTTP client session"""
        try:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers=self.default_headers
            )
            self.logger.info("API client started")
        except Exception as e:
            self.logger.error(f"Failed to start API client: {str(e)}")
            raise
    
    async def close(self) -> None:
        """Close HTTP client session"""
        try:
            if self.session:
                await self.session.close()
            self.logger.info("API client closed")
        except Exception as e:
            self.logger.error(f"Error closing API client: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        if endpoint.startswith(("http://", "https://")):
            return endpoint
        if not self.base_url:
            raise ValueError("Base URL is not set. Please provide base_url when initializing APIRequest or set BASE_URL in environment variables.")
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    async def request(self, method: str, endpoint: str, **kwargs) -> Response:
        """
        Make HTTP request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint
            **kwargs: Request parameters
                - params: Query parameters
                - headers: Request headers
                - json: JSON data
                - data: Form data
                - timeout: Timeout
            
        Returns:
            Response object
        """
        if not self.session:
            raise RuntimeError("API client not started, please call start() method first")
        
        method = method.upper()
        url = self._build_url(endpoint)
        
        try:
            self.logger.info(f"{method} request to: {url}")
            
            async with self.session.request(method, url, **kwargs) as http_response:
                # Read response content
                content = await http_response.read()
                text = content.decode('utf-8', errors='ignore')
                
                # Create response object
                response = Response(
                    status=http_response.status,
                    headers=dict(http_response.headers),
                    content=content,
                    text=text,
                    url=str(http_response.url)
                )
                
                self.logger.info(f"Response received: {http_response.status}")
                return response
                
        except Exception as e:
            self.logger.error(f"Request failed: {method} {endpoint}, error: {str(e)}")
            raise
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, 
                  headers: Optional[Dict] = None, **kwargs) -> Response:
        """Make GET request"""
        return await self.request("GET", endpoint, params=params, headers=headers, **kwargs)
    
    async def post(self, endpoint: str, json: Optional[Dict] = None, 
                   data: Optional[Union[Dict, str]] = None,
                   params: Optional[Dict] = None,
                   headers: Optional[Dict] = None, **kwargs) -> Response:
        """Make POST request"""
        return await self.request("POST", endpoint, json=json, data=data, 
                                 params=params, headers=headers, **kwargs)
    
    async def put(self, endpoint: str, json: Optional[Dict] = None,
                  data: Optional[Union[Dict, str]] = None,
                  params: Optional[Dict] = None,
                  headers: Optional[Dict] = None, **kwargs) -> Response:
        """Make PUT request"""
        return await self.request("PUT", endpoint, json=json, data=data,
                                 params=params, headers=headers, **kwargs)
    
    async def delete(self, endpoint: str, params: Optional[Dict] = None,
                     headers: Optional[Dict] = None, **kwargs) -> Response:
        """Make DELETE request"""
        return await self.request("DELETE", endpoint, params=params, headers=headers, **kwargs)
    
    async def patch(self, endpoint: str, json: Optional[Dict] = None,
                    data: Optional[Union[Dict, str]] = None,
                    params: Optional[Dict] = None,
                    headers: Optional[Dict] = None, **kwargs) -> Response:
        """Make PATCH request"""
        return await self.request("PATCH", endpoint, json=json, data=data,
                                 params=params, headers=headers, **kwargs)
    
    def set_header(self, key: str, value: str) -> None:
        """Set default header"""
        self.default_headers[key] = value
        if self.session:
            self.session.headers.update({key: value})
    
    def set_auth(self, auth_type: str, credentials: Union[str, tuple]) -> None:
        """Set authentication"""
        if auth_type.lower() == "bearer":
            self.set_header("Authorization", f"Bearer {credentials}")
        elif auth_type.lower() == "basic":
            import base64
            if isinstance(credentials, tuple):
                username, password = credentials
                encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
                self.set_header("Authorization", f"Basic {encoded}")
        elif auth_type.lower() == "api_key":
            if isinstance(credentials, tuple):
                key, value = credentials
                self.set_header(key, value)
