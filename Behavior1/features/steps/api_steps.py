"""
API Test Steps - Defines BDD steps for API testing
"""

import asyncio
import json
import os
from pathlib import Path
from behave import given, when, then, step
from behavior_framework.api.request import APIRequest
from behavior_framework.api.assertions import APIAssertions
from behavior_framework.utils.logger import Logger
from behavior_framework.utils.file_reader import FileReader

logger = Logger()
file_reader = FileReader()


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
    Example: api_config.base_url -> yaml_data['api_config']['base_url']
    """
    keys = path.split('.')
    value = yaml_data
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise KeyError(f"Path '{path}' not found in YAML data. Key '{key}' not found.")
    
    return value


@given('I initialize API client with base URL "{base_url}"')
def step_init_api_client(context, base_url):
    """Initialize API client"""
    context.api_client = APIRequest(base_url=base_url)
    run_in_loop(context, context.api_client.start())
    logger.info(f"API client initialized, base URL: {base_url}")


@given('I initialize API client with config file "{config_file}" and value "{yaml_path}"')
def step_init_api_client_from_yaml(context, config_file, yaml_path):
    """
    Initialize API client with base URL from YAML configuration file
    Args:
        config_file: YAML config file name (e.g., "api_config.yaml")
        yaml_path: Path to value in YAML file using dot notation (e.g., "api_config.base_url")
    """
    # Read YAML config file from data/api directory
    api_data_dir = context.settings.api_data_dir
    config_file_path = Path(api_data_dir) / config_file
    
    if not config_file_path.exists():
        raise FileNotFoundError(f"API config file not found: {config_file_path}")
    
    # Read YAML file
    config_data = file_reader.read_yaml(str(config_file_path))
    
    # Get base_url from YAML using path
    try:
        base_url = get_value_from_yaml_path(config_data, yaml_path)
    except KeyError as e:
        raise ValueError(f"Path '{yaml_path}' not found in config file '{config_file}': {str(e)}")
    
    if not base_url:
        raise ValueError(f"base_url is empty in config file '{config_file}' at path '{yaml_path}'")
    
    # Store config data in context for later use (e.g., endpoints)
    context.api_config = config_data
    
    context.api_client = APIRequest(base_url=base_url)
    run_in_loop(context, context.api_client.start())
    logger.info(f"API client initialized from config file: {config_file}, path: {yaml_path}, base URL: {base_url}")


@given('I initialize API client with configured base URL')
def step_init_api_client_from_config(context):
    """Initialize API client with base URL from environment configuration (deprecated, use config file instead)"""
    base_url = context.settings.api_base_url or context.settings.base_url
    if not base_url:
        raise ValueError("API base URL not configured. Please set API_BASE_URL or BASE_URL in environment variables.")
    context.api_client = APIRequest(base_url=base_url)
    run_in_loop(context, context.api_client.start())
    logger.info(f"API client initialized, base URL: {base_url}")


@given('I set API request header "{header_name}" to "{header_value}"')
def step_set_api_header(context, header_name, header_value):
    """Set API request header"""
    if not hasattr(context, 'api_headers'):
        context.api_headers = {}
    context.api_headers[header_name] = header_value
    logger.info(f"Set request header: {header_name} = {header_value}")


@given('I set API authentication as "{auth_type}" with credentials "{credentials}"')
def step_set_api_auth(context, auth_type, credentials):
    """Set API authentication"""
    context.api_client.set_auth(auth_type, credentials)
    logger.info(f"Set API authentication: {auth_type}")


# More specific steps first to avoid ambiguity
@when('I send "{method}" request to "{endpoint}" with JSON file "{json_file}"')
def step_send_request_with_json_file(context, method, endpoint, json_file):
    """Send HTTP request with body from JSON file"""
    headers = getattr(context, 'api_headers', {})
    params = getattr(context, 'api_params', {})
    
    # Read JSON file from data/api directory
    api_data_dir = context.settings.api_data_dir
    json_path = Path(api_data_dir) / json_file
    
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    request_body = file_reader.read_json(str(json_path))
    
    # Build full URL for evidence
    full_url = context.api_client._build_url(endpoint)
    if params:
        import urllib.parse
        full_url += '?' + urllib.parse.urlencode(params)
    
    response = run_in_loop(context, context.api_client.request(
        method=method,
        endpoint=endpoint,
        headers=headers,
        params=params,
        json=request_body
    ))
    
    context.response = response
    
    # Save evidence
    if hasattr(context, 'evidence_manager'):
        response_body = response.json() if response.is_json() else response.text
        context.evidence_manager.add_api_request(
            method=method,
            url=full_url,
            headers=headers,
            body=request_body,
            response_status=response.status,
            response_headers=response.headers,
            response_body=response_body
        )
    
    logger.info(f"Sent {method} request to: {endpoint}, body from file: {json_file}")


@when('I send "{method}" request to "{endpoint}" with request body')
def step_send_request_with_body(context, method, endpoint):
    """Send HTTP request with body"""
    headers = getattr(context, 'api_headers', {})
    params = getattr(context, 'api_params', {})
    
    # Parse request body
    try:
        request_body = json.loads(context.text)
    except json.JSONDecodeError:
        request_body = context.text
    
    # Build full URL for evidence
    full_url = context.api_client._build_url(endpoint)
    if params:
        import urllib.parse
        full_url += '?' + urllib.parse.urlencode(params)
    
    response = run_in_loop(context, context.api_client.request(
        method=method,
        endpoint=endpoint,
        headers=headers,
        params=params,
        json=request_body if isinstance(request_body, dict) else None,
        data=request_body if not isinstance(request_body, dict) else None
    ))
    
    context.response = response
    
    # Save evidence
    if hasattr(context, 'evidence_manager'):
        response_body = response.json() if response.is_json() else response.text
        context.evidence_manager.add_api_request(
            method=method,
            url=full_url,
            headers=headers,
            body=request_body,
            response_status=response.status,
            response_headers=response.headers,
            response_body=response_body
        )
    
    logger.info(f"Sent {method} request to: {endpoint}, body: {request_body}")


@when('I send "{method}" request to "{endpoint}" with query parameters')
def step_send_request_with_params(context, method, endpoint):
    """Send HTTP request with query parameters"""
    headers = getattr(context, 'api_headers', {})
    
    # Parse query parameters
    params = {}
    for row in context.table:
        key = row['key']
        value = row['value']
        params[key] = value
    
    context.api_params = params
    
    # Build full URL for evidence
    full_url = context.api_client._build_url(endpoint)
    if params:
        import urllib.parse
        full_url += '?' + urllib.parse.urlencode(params)
    
    response = run_in_loop(context, context.api_client.request(
        method=method,
        endpoint=endpoint,
        headers=headers,
        params=params
    ))
    
    context.response = response
    
    # Save evidence
    if hasattr(context, 'evidence_manager'):
        response_body = response.json() if response.is_json() else response.text
        context.evidence_manager.add_api_request(
            method=method,
            url=full_url,
            headers=headers,
            body=None,
            response_status=response.status,
            response_headers=response.headers,
            response_body=response_body
        )
    
    logger.info(f"Sent {method} request to: {endpoint}, params: {params}")


@when('I send "{method}" request to "{endpoint}"')
def step_send_request(context, method, endpoint):
    """Send HTTP request"""
    headers = getattr(context, 'api_headers', {})
    params = getattr(context, 'api_params', {})
    
    # Build full URL for evidence
    full_url = context.api_client._build_url(endpoint)
    if params:
        import urllib.parse
        full_url += '?' + urllib.parse.urlencode(params)
    
    response = run_in_loop(context, context.api_client.request(
        method=method,
        endpoint=endpoint,
        headers=headers,
        params=params
    ))
    
    context.response = response
    
    # Save evidence
    if hasattr(context, 'evidence_manager'):
        response_body = response.json() if response.is_json() else response.text
        context.evidence_manager.add_api_request(
            method=method,
            url=full_url,
            headers=headers,
            body=None,
            response_status=response.status,
            response_headers=response.headers,
            response_body=response_body
        )
    
    logger.info(f"Sent {method} request to: {endpoint}")


@then('the response status code should be "{expected_status}"')
def step_assert_status(context, expected_status):
    """Assert response status code"""
    expected_status = int(expected_status)
    assertions = APIAssertions(context.response)
    assertions.assert_status(expected_status)


@then('the response status code should be successful')
def step_assert_success(context):
    """Assert response is successful"""
    assertions = APIAssertions(context.response)
    assertions.assert_success()


@then('the response header "{header_name}" should be "{expected_value}"')
def step_assert_header(context, header_name, expected_value):
    """Assert response header"""
    assertions = APIAssertions(context.response)
    assertions.assert_header(header_name, expected_value)


@then('the response JSON value for "{key}" should be "{expected_value}"')
def step_assert_json_value(context, key, expected_value):
    """Assert JSON response value"""
    # Try to convert expected value to appropriate type
    try:
        if expected_value.isdigit():
            expected_value = int(expected_value)
        elif expected_value.lower() in ('true', 'false'):
            expected_value = expected_value.lower() == 'true'
    except:
        pass
    
    assertions = APIAssertions(context.response)
    assertions.assert_json(key, expected_value)


@then('the response should contain text "{expected_text}"')
def step_assert_text(context, expected_text):
    """Assert response text"""
    assertions = APIAssertions(context.response)
    assertions.assert_text(expected_text)


@then('the response should be in JSON format')
def step_assert_json_format(context):
    """Assert response is JSON format"""
    if not context.response.is_json():
        raise AssertionError("Response is not JSON format")


@then('I save the response JSON value for "{key}" as "{variable_name}"')
def step_save_json_value(context, key, variable_name):
    """Save JSON response value to context variable"""
    if not hasattr(context, 'variables'):
        context.variables = {}
    
    value = context.response.get_json_value(key)
    context.variables[variable_name] = value
    logger.info(f"Saved variable: {variable_name} = {value}")
