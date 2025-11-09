"""
UI Test Example - Example of using Behavior Framework for UI testing
This file is for reference only, actual test cases should be written in .feature files in the features directory
"""

import asyncio
from behavior_framework.ui.page import Browser
from behavior_framework.config.settings import Settings


async def example_ui_test():
    """UI test example"""
    settings = Settings()
    
    # Open browser
    async with Browser(settings) as browser:
        # Create page (specify page name to use YAML element location)
        page = await browser.new_page(page_name="example_page")
        
        # Navigate to page
        await page.goto("https://example.com")
        
        # Get element (read from YAML configuration)
        heading = page.get_element_by_name("heading")
        
        # Verify element is visible
        is_visible = await heading.is_visible()
        assert is_visible, "Heading element is not visible"
        
        # Get text
        text = await heading.text_content()
        print(f"Page title: {text}")
        
        print("UI test passed")


if __name__ == "__main__":
    asyncio.run(example_ui_test())
