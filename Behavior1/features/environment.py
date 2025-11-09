"""
Behave Environment Configuration - Defines pre and post processing for test execution
"""

import asyncio
import os
import allure
from pathlib import Path
from behavior_framework.config.settings import Settings
from behavior_framework.ui.page import Browser
from behavior_framework.api.request import APIRequest
from behavior_framework.utils.logger import Logger
from behavior_framework.utils.evidence import EvidenceManager

logger = Logger()
settings = Settings()


def before_all(context):
    """Execute before all tests start"""
    try:
        logger.info("=" * 50)
        logger.info("Starting test suite execution")
        logger.info("=" * 50)
        context.settings = settings
        context.logger = logger
        context.browser = None
        context.api_client = None
        
        # Create Allure report directory
        allure_dir = Path("allure-results")
        allure_dir.mkdir(exist_ok=True)
        
        # Initialize evidence manager
        evidence_dir = os.getenv("EVIDENCE_DIR", "evidence")
        context.evidence_manager = EvidenceManager(evidence_dir=evidence_dir)
        
        # Initialize event loop for async operations
        # Create a new event loop for each test run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        context.event_loop = loop
    except Exception as e:
        logger.error(f"Error in before_all: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def after_all(context):
    """Execute after all tests complete"""
    logger.info("=" * 50)
    logger.info("Test suite execution completed")
    logger.info("=" * 50)
    
    # Close event loop
    if hasattr(context, 'event_loop'):
        try:
            loop = context.event_loop
            if not loop.is_closed():
                # Wait for pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
        except Exception as e:
            logger.error(f"Error closing event loop: {str(e)}")


def before_feature(context, feature):
    """Execute before each feature starts"""
    logger.info(f"Starting Feature execution: {feature.name}")
    context.feature_name = feature.name


def after_feature(context, feature):
    """Execute after each feature completes"""
    logger.info(f"Feature execution completed: {feature.name}")


def before_scenario(context, scenario):
    """Execute before each scenario starts"""
    logger.info(f"Starting Scenario execution: {scenario.name}")
    context.scenario_name = scenario.name
    # Use scenario_tags instead of tags to avoid context masking warning
    if hasattr(scenario, 'tags'):
        context.scenario_tags = scenario.tags
    context.browser = None
    context.api_client = None
    context.page = None
    context.response = None
    
    # Initialize evidence for this scenario
    feature_name = getattr(context, 'feature_name', 'Unknown')
    context.evidence_manager.start_scenario(feature_name, scenario.name)


def after_scenario(context, scenario):
    """Execute after each scenario completes"""
    logger.info(f"Scenario execution completed: {scenario.name}")
    
    # Save evidence for this scenario
    if hasattr(context, 'evidence_manager'):
        evidence_path = context.evidence_manager.save_evidence()
        if evidence_path:
            logger.info(f"Test evidence saved to: {evidence_path}")
            # Attach evidence to Allure report
            try:
                allure.attach.file(
                    str(evidence_path),
                    name="Test Evidence",
                    attachment_type=allure.attachment_type.JSON
                )
            except Exception as e:
                logger.warning(f"Failed to attach evidence to Allure: {str(e)}")
    
    # Cleanup resources
    loop = context.event_loop if hasattr(context, 'event_loop') else None
    
    if hasattr(context, 'api_client') and context.api_client:
        try:
            if loop and not loop.is_closed():
                loop.run_until_complete(context.api_client.close())
            else:
                asyncio.run(context.api_client.close())
        except Exception as e:
            logger.error(f"Failed to close API client: {str(e)}")
        context.api_client = None
    
    if hasattr(context, 'browser') and context.browser:
        try:
            if loop and not loop.is_closed():
                loop.run_until_complete(context.browser.close())
            else:
                asyncio.run(context.browser.close())
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
        context.browser = None


def before_step(context, step):
    """Execute before each step starts"""
    logger.debug(f"Executing Step: {step.name}")


def after_step(context, step):
    """Execute after each step completes"""
    if step.status == "failed":
        logger.error(f"Step execution failed: {step.name}")
        # Add screenshot on failure
        if hasattr(context, 'browser') and context.browser:
            try:
                loop = context.event_loop if hasattr(context, 'event_loop') else None
                if loop and not loop.is_closed():
                    page = loop.run_until_complete(context.browser.new_page())
                    screenshot_path = f"allure-results/screenshot_{context.scenario_name}_{step.name}.png"
                    loop.run_until_complete(page.screenshot(screenshot_path))
                    allure.attach.file(screenshot_path, name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                logger.error(f"Screenshot failed: {str(e)}")
