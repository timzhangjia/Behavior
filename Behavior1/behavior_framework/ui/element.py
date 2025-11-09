"""
Element Management Module - Provides element-level operations and assertion functionality
"""

from typing import Optional, List, Dict, Any, Union
from playwright.async_api import Locator
from ..utils.logger import Logger


class Element:
    """Element manager, wraps Playwright element operations"""
    
    def __init__(self, locator: Locator, timeout: int, logger: Logger):
        self.locator = locator
        self.timeout = timeout
        self.logger = logger
    
    async def click(self, force: bool = False, timeout: Optional[int] = None) -> None:
        """Click element"""
        try:
            timeout = timeout or self.timeout
            await self.locator.click(force=force, timeout=timeout)
            self.logger.info(f"Element clicked: {self.locator}")
        except Exception as e:
            self.logger.error(f"Click failed: {str(e)}")
            raise
    
    async def double_click(self, timeout: Optional[int] = None) -> None:
        """Double click element"""
        try:
            timeout = timeout or self.timeout
            await self.locator.dblclick(timeout=timeout)
            self.logger.info(f"Element double clicked: {self.locator}")
        except Exception as e:
            self.logger.error(f"Double click failed: {str(e)}")
            raise
    
    async def right_click(self, timeout: Optional[int] = None) -> None:
        """Right click element"""
        try:
            timeout = timeout or self.timeout
            await self.locator.click(button="right", timeout=timeout)
            self.logger.info(f"Element right clicked: {self.locator}")
        except Exception as e:
            self.logger.error(f"Right click failed: {str(e)}")
            raise
    
    async def type(self, text: str, delay: int = 100, timeout: Optional[int] = None) -> None:
        """Type text into element"""
        try:
            timeout = timeout or self.timeout
            await self.locator.fill(text, timeout=timeout)
            self.logger.info(f"Text typed: {text}")
        except Exception as e:
            self.logger.error(f"Type failed: {str(e)}")
            raise
    
    async def type_slowly(self, text: str, delay: int = 100, timeout: Optional[int] = None) -> None:
        """Type text slowly (simulate real user input)"""
        try:
            timeout = timeout or self.timeout
            await self.locator.type(text, delay=delay, timeout=timeout)
            self.logger.info(f"Text typed slowly: {text}")
        except Exception as e:
            self.logger.error(f"Slow type failed: {str(e)}")
            raise
    
    async def clear(self, timeout: Optional[int] = None) -> None:
        """Clear element content"""
        try:
            timeout = timeout or self.timeout
            await self.locator.clear(timeout=timeout)
            self.logger.info("Element content cleared")
        except Exception as e:
            self.logger.error(f"Clear failed: {str(e)}")
            raise
    
    async def hover(self, timeout: Optional[int] = None) -> None:
        """Hover over element"""
        try:
            timeout = timeout or self.timeout
            await self.locator.hover(timeout=timeout)
            self.logger.info(f"Element hovered: {self.locator}")
        except Exception as e:
            self.logger.error(f"Hover failed: {str(e)}")
            raise
    
    async def wait_for(self, state: str = "visible", timeout: Optional[int] = None) -> None:
        """Wait for element state"""
        try:
            timeout = timeout or self.timeout
            await self.locator.wait_for(state=state, timeout=timeout)
            self.logger.debug(f"Element state changed to: {state}")
        except Exception as e:
            self.logger.error(f"Wait for element state failed: {str(e)}")
            raise
    
    async def wait_for_visible(self, timeout: Optional[int] = None) -> None:
        """Wait for element to be visible"""
        try:
            timeout = timeout or self.timeout
            await self.locator.wait_for(state="visible", timeout=timeout)
            self.logger.debug("Element is now visible")
        except Exception as e:
            self.logger.error(f"Wait for element visible failed: {str(e)}")
            raise
    
    async def is_visible(self, timeout: Optional[int] = None) -> bool:
        """Check if element is visible"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.is_visible(timeout=timeout)
        except Exception as e:
            self.logger.error(f"Check element visibility failed: {str(e)}")
            return False
    
    async def is_enabled(self, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.is_enabled(timeout=timeout)
        except Exception as e:
            self.logger.error(f"Check element enabled state failed: {str(e)}")
            return False
    
    async def is_checked(self, timeout: Optional[int] = None) -> bool:
        """Check if element is checked"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.is_checked(timeout=timeout)
        except Exception as e:
            self.logger.error(f"Check element checked state failed: {str(e)}")
            return False
    
    async def text_content(self, timeout: Optional[int] = None) -> Optional[str]:
        """Get element text content"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.text_content(timeout=timeout)
        except Exception as e:
            self.logger.error(f"Get element text failed: {str(e)}")
            return None
    
    async def inner_text(self, timeout: Optional[int] = None) -> Optional[str]:
        """Get element inner text"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.inner_text(timeout=timeout)
        except Exception as e:
            self.logger.error(f"Get element inner text failed: {str(e)}")
            return None
    
    async def get_attribute(self, name: str, timeout: Optional[int] = None) -> Optional[str]:
        """Get element attribute value"""
        try:
            timeout = timeout or self.timeout
            return await self.locator.get_attribute(name, timeout=timeout)
        except Exception as e:
            self.logger.error(f"Get element attribute failed: {str(e)}")
            return None
    
    async def count(self) -> int:
        """Get count of matching elements"""
        try:
            return await self.locator.count()
        except Exception as e:
            self.logger.error(f"Get element count failed: {str(e)}")
            return 0
    
    def nth(self, index: int) -> "Element":
        """Get nth matching element"""
        return Element(self.locator.nth(index), self.timeout, self.logger)
    
    def first(self) -> "Element":
        """Get first matching element"""
        return Element(self.locator.first, self.timeout, self.logger)
    
    def last(self) -> "Element":
        """Get last matching element"""
        return Element(self.locator.last, self.timeout, self.logger)
