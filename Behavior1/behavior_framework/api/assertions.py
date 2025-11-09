"""
API Assertions Module - Provides API response assertion functionality
"""

from typing import Optional, Union, Dict, Any
from .request import Response
from ..utils.logger import Logger
import allure


class APIAssertions:
    """API assertion class with chainable methods"""
    
    def __init__(self, response: Response):
        """
        Initialize assertion class
        
        Args:
            response: Response object
        """
        self.response = response
        self.logger = Logger()
    
    def assert_status(self, expected_status: Union[int, list], message: Optional[str] = None) -> "APIAssertions":
        """
        Assert response status code
        
        Args:
            expected_status: Expected status code or list of status codes
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        expected_statuses = expected_status if isinstance(expected_status, list) else [expected_status]
        
        if self.response.status not in expected_statuses:
            error_msg = message or f"Status assertion failed: expected {expected_statuses}, actual {self.response.status}"
            self.logger.error(error_msg)
            allure.attach(self.response.text, name="Response Content", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(error_msg)
        
        self.logger.info(f"Status assertion passed: {self.response.status}")
        return self
    
    def assert_header(self, header_name: str, expected_value: Optional[str] = None, 
                     message: Optional[str] = None) -> "APIAssertions":
        """
        Assert response header
        
        Args:
            header_name: Header name
            expected_value: Expected header value, if None only checks existence
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        actual_value = self.response.get_header(header_name)
        
        if expected_value is None:
            if actual_value is None:
                error_msg = message or f"Header does not exist: {header_name}"
                self.logger.error(error_msg)
                raise AssertionError(error_msg)
        else:
            if actual_value != expected_value:
                error_msg = message or f"Header value mismatch: {header_name}, expected {expected_value}, actual {actual_value}"
                self.logger.error(error_msg)
                raise AssertionError(error_msg)
        
        self.logger.info(f"Header assertion passed: {header_name}")
        return self
    
    def assert_json(self, key: str, expected_value: Any = None, message: Optional[str] = None) -> "APIAssertions":
        """
        Assert JSON response value
        
        Args:
            key: JSON key name, supports nested keys with dot notation (e.g., "user.name")
            expected_value: Expected value, if None only checks key existence
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        if not self.response.is_json():
            error_msg = message or "Response is not JSON format"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        
        actual_value = self.response.get_json_value(key)
        
        if expected_value is None:
            if actual_value is None:
                error_msg = message or f"JSON key does not exist: {key}"
                self.logger.error(error_msg)
                raise AssertionError(error_msg)
        else:
            if actual_value != expected_value:
                error_msg = message or f"JSON value mismatch: {key}, expected {expected_value}, actual {actual_value}"
                self.logger.error(error_msg)
                allure.attach(str(self.response.json()), name="JSON Response", attachment_type=allure.attachment_type.JSON)
                raise AssertionError(error_msg)
        
        self.logger.info(f"JSON assertion passed: {key}")
        return self
    
    def assert_text(self, expected_text: str, exact: bool = False, message: Optional[str] = None) -> "APIAssertions":
        """
        Assert response text
        
        Args:
            expected_text: Expected text
            exact: Whether to match exactly
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        if exact:
            is_match = self.response.text == expected_text
        else:
            is_match = expected_text in self.response.text
        
        if not is_match:
            error_msg = message or f"Text assertion failed: expected to contain '{expected_text}'"
            self.logger.error(error_msg)
            allure.attach(self.response.text, name="Response Text", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(error_msg)
        
        self.logger.info(f"Text assertion passed: {expected_text}")
        return self
    
    def assert_success(self, message: Optional[str] = None) -> "APIAssertions":
        """
        Assert response is successful (2xx status)
        
        Args:
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        if not self.response.is_success():
            error_msg = message or f"Response is not successful: status {self.response.status}"
            self.logger.error(error_msg)
            allure.attach(self.response.text, name="Error Response", attachment_type=allure.attachment_type.TEXT)
            raise AssertionError(error_msg)
        
        self.logger.info("Success assertion passed")
        return self
    
    def assert_json_schema(self, schema: Dict[str, Any], message: Optional[str] = None) -> "APIAssertions":
        """
        Assert JSON schema (simple implementation)
        
        Args:
            schema: JSON schema dictionary
            message: Custom error message
            
        Returns:
            self, supports chaining
        """
        if not self.response.is_json():
            error_msg = message or "Response is not JSON format"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        
        json_data = self.response.json()
        missing_keys = []
        
        for key in schema.keys():
            if key not in json_data:
                missing_keys.append(key)
        
        if missing_keys:
            error_msg = message or f"JSON schema validation failed: missing keys {missing_keys}"
            self.logger.error(error_msg)
            raise AssertionError(error_msg)
        
        self.logger.info("JSON schema assertion passed")
        return self


# Backward compatibility assertion classes
class ShouldHaveStatus:
    """Response should have specified status code assertion (backward compatible)"""
    
    def __init__(self, response: Response, expected_status: Union[int, list]):
        self.response = response
        self.expected_status = expected_status if isinstance(expected_status, list) else [expected_status]
        self.logger = Logger()
    
    async def execute(self) -> bool:
        """Execute status assertion"""
        try:
            assertions = APIAssertions(self.response)
            assertions.assert_status(self.expected_status)
            return True
        except AssertionError:
            return False


class ShouldHaveHeader:
    """Response should have specified header assertion (backward compatible)"""
    
    def __init__(self, response: Response, header_name: str, expected_value: Optional[str] = None):
        self.response = response
        self.header_name = header_name
        self.expected_value = expected_value
        self.logger = Logger()
    
    async def execute(self) -> bool:
        """Execute header assertion"""
        try:
            assertions = APIAssertions(self.response)
            assertions.assert_header(self.header_name, self.expected_value)
            return True
        except AssertionError:
            return False


class ShouldHaveJson:
    """Response should have specified JSON value assertion (backward compatible)"""
    
    def __init__(self, response: Response, key: str, expected_value: Any = None):
        self.response = response
        self.key = key
        self.expected_value = expected_value
        self.logger = Logger()
    
    async def execute(self) -> bool:
        """Execute JSON assertion"""
        try:
            assertions = APIAssertions(self.response)
            assertions.assert_json(self.key, self.expected_value)
            return True
        except AssertionError:
            return False


class ShouldBeSuccess:
    """Response should be successful (2xx status) assertion (backward compatible)"""
    
    def __init__(self, response: Response):
        self.response = response
        self.logger = Logger()
    
    async def execute(self) -> bool:
        """Execute success assertion"""
        try:
            assertions = APIAssertions(self.response)
            assertions.assert_success()
            return True
        except AssertionError:
            return False
