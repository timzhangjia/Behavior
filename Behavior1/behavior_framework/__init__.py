"""
Behavior Framework - Python UI and API Automation Testing Framework

A clean and powerful framework for both UI and API automation testing.
"""

__version__ = "1.0.0"
__author__ = "Behavior Framework Team"

# UI Testing Components
from .ui.page import Browser, Page
from .ui.element import Element

# API Testing Components
from .api.request import APIRequest, Response
from .api.assertions import APIAssertions, ShouldHaveStatus, ShouldHaveHeader, ShouldHaveJson, ShouldBeSuccess

# Common Components
from .config.settings import Settings
from .utils.logger import Logger

__all__ = [
    # UI Testing
    "Browser",
    "Page", 
    "Element",
    
    # API Testing
    "APIRequest",
    "Response",
    "APIAssertions",
    "ShouldHaveStatus",
    "ShouldHaveHeader",
    "ShouldHaveJson",
    "ShouldBeSuccess",
    
    # Common
    "Settings",
    "Logger"
]
