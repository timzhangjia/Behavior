"""
UI Test Steps - Defines BDD steps for UI testing
"""

import asyncio
from datetime import datetime
from pathlib import Path
from behave import given, when, then, step
from behavior_framework.ui.page import Browser
from behavior_framework.utils.logger import Logger
from behavior_framework.utils.file_reader import FileReader

logger = Logger()
file_reader = FileReader()


def _take_page_screenshot(context, page_name: str, page_url: str, description: str = ""):
    """
    Take screenshot of current page and add to evidence
    
    Args:
        context: Behave context
        page_name: Name of the page
        page_url: URL of the page
        description: Description of the screenshot
    """
    if not hasattr(context, 'page') or not context.page:
        return
    
    if not hasattr(context, 'evidence_manager'):
        return
    
    try:
        # Generate screenshot filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_page_name = page_name.replace(" ", "_").replace("/", "_")
        screenshot_filename = f"screenshot_{safe_page_name}_{timestamp}.png"
        
        # Save to temporary screenshots directory
        screenshots_dir = context.evidence_manager.screenshots_dir
        screenshot_path = screenshots_dir / screenshot_filename
        
        # Take screenshot
        run_in_loop(context, context.page.screenshot(str(screenshot_path), full_page=True))
        
        # Add to evidence
        context.evidence_manager.add_ui_screenshot(
            screenshot_path=str(screenshot_path),
            description=description or f"Screenshot of {page_name}",
            page_url=page_url
        )
        
        logger.debug(f"Screenshot taken: {screenshot_path}")
    except Exception as e:
        logger.warning(f"Failed to take screenshot: {str(e)}")


def run_in_loop(context, coro):
    """Run coroutine in context event loop"""
    if hasattr(context, 'event_loop'):
        loop = context.event_loop
        if not loop.is_closed():
            try:
                if loop.is_running():
                    # Use nest_asyncio if loop is already running
                    import nest_asyncio
                    nest_asyncio.apply()
                return loop.run_until_complete(coro)
            except RuntimeError:
                pass
    
    # Fallback to asyncio.run if no loop available
    return asyncio.run(coro)


def get_value_from_yaml_path(yaml_data, path):
    """
    Get value from YAML data using dot notation path
    Example: ui_config.example_url -> yaml_data['ui_config']['example_url']
    """
    keys = path.split('.')
    value = yaml_data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise KeyError(f"Path '{path}' not found in YAML data. Key '{key}' not found.")
    
    return value


@given('I open the browser')
def step_open_browser(context):
    """Open browser"""
    context.browser = Browser(context.settings)
    run_in_loop(context, context.browser.start())
    logger.info("Browser opened")


@given('I open page "{page_name}" with URL "{url}"')
def step_open_page(context, page_name, url):
    """Open page"""
    if not hasattr(context, 'browser'):
        step_open_browser(context)
    
    page = run_in_loop(context, context.browser.new_page(page_name=page_name))
    run_in_loop(context, page.goto(url))
    # Wait for page to load
    run_in_loop(context, page.wait_for_load_state("networkidle"))
    context.page = page
    context.current_page_name = page_name
    
    # Take screenshot for evidence
    _take_page_screenshot(context, page_name, url, f"Opened page: {page_name}")
    
    logger.info(f"Opened page: {page_name}, URL: {url}")


@given('I open page "{page_name}" with URL from config "{config_file}" and value "{yaml_path}"')
def step_open_page_from_config(context, page_name, config_file, yaml_path):
    """
    Open page with URL from YAML configuration file
    Args:
        page_name: Page name
        config_file: YAML config file name (e.g., "ui_config.yaml")
        yaml_path: Path to value in YAML file using dot notation (e.g., "ui_config.example_url")
    """
    # Read YAML config file from data/api directory
    api_data_dir = context.settings.api_data_dir
    config_file_path = Path(api_data_dir) / config_file
    
    if not config_file_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file_path}")
    
    # Read YAML file
    config_data = file_reader.read_yaml(str(config_file_path))
    
    # Get URL from YAML using path
    try:
        url = get_value_from_yaml_path(config_data, yaml_path)
    except KeyError as e:
        raise ValueError(f"Path '{yaml_path}' not found in config file '{config_file}': {str(e)}")
    
    if not url:
        raise ValueError(f"URL is empty in config file '{config_file}' at path '{yaml_path}'")
    
    # Open page with URL from config
    if not hasattr(context, 'browser'):
        step_open_browser(context)
    
    page = run_in_loop(context, context.browser.new_page(page_name=page_name))
    run_in_loop(context, page.goto(url))
    # Wait for page to load
    run_in_loop(context, page.wait_for_load_state("networkidle"))
    context.page = page
    context.current_page_name = page_name
    
    # Take screenshot for evidence
    _take_page_screenshot(context, page_name, url, f"Opened page: {page_name} from config")
    
    logger.info(f"Opened page: {page_name}, URL from config file: {config_file}, path: {yaml_path} = {url}")


@when('I navigate to "{url}"')
def step_navigate_to(context, url):
    """Navigate to specified URL"""
    run_in_loop(context, context.page.goto(url))
    # Wait for page to load
    run_in_loop(context, context.page.wait_for_load_state("networkidle"))
    
    # Take screenshot for evidence
    page_name = getattr(context, 'current_page_name', 'unknown_page')
    _take_page_screenshot(context, page_name, url, f"Navigated to: {url}")
    
    logger.info(f"Navigated to: {url}")


@when('I navigate to URL from config "{config_file}" and value "{yaml_path}"')
def step_navigate_to_from_config(context, config_file, yaml_path):
    """
    Navigate to URL from YAML configuration file
    Args:
        config_file: YAML config file name (e.g., "ui_config.yaml")
        yaml_path: Path to value in YAML file using dot notation (e.g., "ui_config.example_url")
    """
    # Read YAML config file from data/api directory
    api_data_dir = context.settings.api_data_dir
    config_file_path = Path(api_data_dir) / config_file
    
    if not config_file_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file_path}")
    
    # Read YAML file
    config_data = file_reader.read_yaml(str(config_file_path))
    
    # Get URL from YAML using path
    try:
        url = get_value_from_yaml_path(config_data, yaml_path)
    except KeyError as e:
        raise ValueError(f"Path '{yaml_path}' not found in config file '{config_file}': {str(e)}")
    
    if not url:
        raise ValueError(f"URL is empty in config file '{config_file}' at path '{yaml_path}'")
    
    run_in_loop(context, context.page.goto(url))
    # Wait for page to load
    run_in_loop(context, context.page.wait_for_load_state("networkidle"))
    
    # Take screenshot for evidence
    page_name = getattr(context, 'current_page_name', 'unknown_page')
    _take_page_screenshot(context, page_name, url, f"Navigated to URL from config")
    
    logger.info(f"Navigated to URL from config file: {config_file}, path: {yaml_path} = {url}")


@when('I type "{text}" into element "{element_name}"')
def step_type_text(context, text, element_name):
    """Type text into element"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        # Try using selector
        element = context.page.get_element(element_name)
    
    # Wait for element to be attached (exists in DOM) before typing
    # Use wait_for attached state instead of visible, as some elements may be hidden but still interactive
    try:
        run_in_loop(context, element.wait_for(timeout=5000))
    except:
        # If wait_for fails, try to proceed anyway
        pass
    
    # Use type_slowly which may work better for some sites
    run_in_loop(context, element.type_slowly(text))
    logger.info(f"Typed text in element {element_name}: {text}")


@when('I click element "{element_name}"')
def step_click_element(context, element_name):
    """Click element"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        # Try using selector
        element = context.page.get_element(element_name)
    
    run_in_loop(context, element.click())
    logger.info(f"Clicked element: {element_name}")


@when('I double click element "{element_name}"')
def step_double_click_element(context, element_name):
    """Double click element"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        element = context.page.get_element(element_name)
    
    run_in_loop(context, element.double_click())
    logger.info(f"Double clicked element: {element_name}")


@when('I hover over element "{element_name}"')
def step_hover_element(context, element_name):
    """Hover over element"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        element = context.page.get_element(element_name)
    
    run_in_loop(context, element.hover())
    logger.info(f"Hovered over element: {element_name}")


@when('I wait for "{seconds}" seconds')
def step_wait_seconds(context, seconds):
    """Wait for specified seconds"""
    run_in_loop(context, asyncio.sleep(int(seconds)))
    logger.info(f"Waited {seconds} seconds")


@when('I wait for the page to load')
def step_wait_page_load(context):
    """Wait for page to load"""
    run_in_loop(context, context.page.wait_for_load_state("networkidle"))
    logger.info("Page load completed")


@then('element "{element_name}" should be visible')
def step_assert_element_visible(context, element_name):
    """Assert element is visible"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        element = context.page.get_element(element_name)
    
    is_visible = run_in_loop(context, element.is_visible())
    assert is_visible, f"Element {element_name} is not visible"
    logger.info(f"Element {element_name} is visible")


@then('element "{element_name}" should contain text "{expected_text}"')
def step_assert_element_text(context, element_name, expected_text):
    """Assert element text"""
    page_name = getattr(context, 'current_page_name', None)
    
    if page_name:
        element = context.page.get_element_by_name(element_name, page_name=page_name)
    else:
        element = context.page.get_element(element_name)
    
    actual_text = run_in_loop(context, element.text_content())
    assert expected_text in actual_text, f"Element {element_name} text does not contain '{expected_text}', actual text: {actual_text}"
    logger.info(f"Element {element_name} contains text: {expected_text}")


@then('the page title should be "{expected_title}"')
def step_assert_page_title(context, expected_title):
    """Assert page title"""
    actual_title = run_in_loop(context, context.page.title())
    assert actual_title == expected_title, f"Page title mismatch, expected: {expected_title}, actual: {actual_title}"
    logger.info(f"Page title: {actual_title}")


@then('the page URL should contain "{expected_url}"')
def step_assert_page_url(context, expected_url):
    """Assert page URL"""
    actual_url = run_in_loop(context, context.page.url())
    assert expected_url in actual_url, f"Page URL does not contain '{expected_url}', actual URL: {actual_url}"
    logger.info(f"Page URL: {actual_url}")


@then('I take a screenshot and save it as "{filename}"')
def step_take_screenshot(context, filename):
    """Take screenshot"""
    run_in_loop(context, context.page.screenshot(filename))
    logger.info(f"Screenshot saved: {filename}")
