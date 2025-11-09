"""
Logging Tool Module - Provides unified logging functionality
"""

import sys
import os
from typing import Optional
from loguru import logger
from ..config.settings import Settings


class Logger:
    """Unified logging manager"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            Logger._initialized = True
    
    def _setup_logger(self, settings: Optional[Settings] = None):
        """Setup logging configuration"""
        # Remove default log handlers
        logger.remove()
        
        # Console output format
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Add console handler
        logger.add(
            sys.stdout,
            format=console_format,
            level="INFO",
            colorize=True
        )
        
        # If file path is set, add file handler
        if settings and settings.logging.file_path:
            logger.add(
                settings.logging.file_path,
                format=settings.logging.format,
                level=settings.logging.level,
                rotation=settings.logging.max_file_size,
                retention=settings.logging.backup_count,
                compression="zip"
            )
    
    def debug(self, message: str, **kwargs):
        """Debug log"""
        logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info log"""
        logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning log"""
        logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error log"""
        logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical error log"""
        logger.critical(message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Success log"""
        logger.success(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Exception log"""
        logger.exception(message, **kwargs)
    
    def bind(self, **kwargs):
        """Bind context variables"""
        return logger.bind(**kwargs)
    
    def patch(self, record):
        """Patch function for custom log recording"""
        record["extra"]["serialized"] = self._serialize(record)
    
    def _serialize(self, record):
        """Serialize log record"""
        subset = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
            "function": record["function"],
            "line": record["line"]
        }
        return subset
    
    @classmethod
    def configure(cls, settings: Settings):
        """Configure logger"""
        instance = cls()
        instance._setup_logger(settings)
        return instance
