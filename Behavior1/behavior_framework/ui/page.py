"""
Page Management Module - Provides page-level operations, browser management and element location functionality
"""

from typing import Optional, List, Union
from playwright.async_api import (
    async_playwright, 
    Page as PlaywrightPage, 
    Browser as PlaywrightBrowser, 
    BrowserContext,
    Locator
)
from .element import Element
from ..config.settings import Settings
from ..utils.logger import Logger
from ..utils.file_reader import ElementLocator


class Browser:
    """Browser manager, wraps Playwright browser operations"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.playwright = None
        self.browser: Optional[PlaywrightBrowser] = None
        self.context: Optional[BrowserContext] = None
        self.logger = Logger()
        
    async def start(self, headless: Optional[bool] = None, browser_type: str = "chromium") -> None:
        """Start browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser type
            if browser_type.lower() == "firefox":
                browser_launcher = self.playwright.firefox
            elif browser_type.lower() == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                browser_launcher = self.playwright.chromium
            
            # Launch browser
            self.browser = await browser_launcher.launch(
                headless=headless if headless is not None else self.settings.headless,
                args=self.settings.browser_args
            )
            
            # Create browser context
            self.context = await self.browser.new_context(
                viewport={
                    "width": self.settings.viewport.width,
                    "height": self.settings.viewport.height
                },
                user_agent=self.settings.user_agent,
                locale=self.settings.locale,
                timezone_id=self.settings.timezone
            )
            
            self.logger.info(f"Browser started: {browser_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            raise
    
    async def new_page(self, page_name: Optional[str] = None) -> "Page":
        """Create new page"""
        if not self.context:
            raise RuntimeError("Browser not started, please call start() method first")
        
        playwright_page = await self.context.new_page()
        page = Page(playwright_page, self.settings, page_name=page_name)
        self.logger.info(f"New page created: {page_name or 'default'}")
        return page
    
    async def close(self) -> None:
        """Close browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


class Page:
    """Page manager, wraps Playwright page operations"""
    
    def __init__(self, playwright_page: PlaywrightPage, settings: Settings, page_name: Optional[str] = None):
        self.page = playwright_page
        self.settings = settings
        self.logger = Logger()
        self.page_name = page_name
        self.element_locator = ElementLocator() if page_name else None
    
    async def goto(self, url: str, wait_until: str = "domcontentloaded") -> None:
        """Navigate to specified URL"""
        try:
            await self.page.goto(url, wait_until=wait_until)
            self.logger.info(f"Navigated to: {url}")
        except Exception as e:
            self.logger.error(f"Navigation failed: {str(e)}")
            raise
    
    async def reload(self, wait_until: str = "domcontentloaded") -> None:
        """Reload page"""
        try:
            await self.page.reload(wait_until=wait_until)
            self.logger.info("Page reloaded")
        except Exception as e:
            self.logger.error(f"Reload failed: {str(e)}")
            raise
    
    async def wait_for_load_state(self, state: str = "domcontentloaded") -> None:
        """Wait for page load state"""
        try:
            await self.page.wait_for_load_state(state)
            self.logger.debug(f"Page state loaded: {state}")
        except Exception as e:
            self.logger.error(f"Failed to wait for page load: {str(e)}")
            raise
    
    def get_element(self, selector: str, timeout: Optional[int] = None) -> Element:
        """Get element by selector"""
        timeout = timeout or self.settings.default_timeout
        locator = self.page.locator(selector)
        return Element(locator, timeout, self.logger)
    
    def get_element_by_name(self, element_name: str, timeout: Optional[int] = None, page_name: Optional[str] = None) -> Element:
        """
        Get element by name from YAML configuration file
        
        Args:
            element_name: Element name (key defined in YAML file)
            timeout: Timeout value
            page_name: Page name, if not provided uses self.page_name
            
        Returns:
            Element object
        """
        if not self.element_locator:
            raise ValueError("Page name not set, cannot use element location feature")
        
        page = page_name or self.page_name
        selector = self.element_locator.get_selector(page, element_name)
        
        if not selector:
            raise ValueError(f"Element location information not found: {page}.{element_name}")
        
        self.logger.debug(f"Get element from config: {page}.{element_name} -> {selector}")
        return self.get_element(selector, timeout)
    
    def get_element_by_text(self, text: str, timeout: Optional[int] = None) -> Element:
        """Get element by text"""
        timeout = timeout or self.settings.default_timeout
        locator = self.page.get_by_text(text)
        return Element(locator, timeout, self.logger)
    
    def get_element_by_role(self, role: str, name: Optional[str] = None, timeout: Optional[int] = None) -> Element:
        """Get element by role"""
        timeout = timeout or self.settings.default_timeout
        locator = self.page.get_by_role(role, name=name)
        return Element(locator, timeout, self.logger)
    
    def get_element_by_placeholder(self, placeholder: str, timeout: Optional[int] = None) -> Element:
        """Get element by placeholder"""
        timeout = timeout or self.settings.default_timeout
        locator = self.page.get_by_placeholder(placeholder)
        return Element(locator, timeout, self.logger)
    
    async def screenshot(self, path: str, full_page: bool = False) -> None:
        """Take page screenshot"""
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            self.logger.info(f"Screenshot saved: {path}")
        except Exception as e:
            self.logger.error(f"Screenshot failed: {str(e)}")
            raise
    
    async def title(self) -> str:
        """Get page title"""
        return await self.page.title()
    
    async def url(self) -> str:
        """Get current URL"""
        return self.page.url
    
    async def evaluate(self, expression: str) -> any:
        """Execute JavaScript expression in page context"""
        try:
            result = await self.page.evaluate(expression)
            self.logger.debug(f"JavaScript executed: {expression}")
            return result
        except Exception as e:
            self.logger.error(f"JavaScript execution failed: {str(e)}")
            raise
