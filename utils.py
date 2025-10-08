"""
Utility functions for error handling and logging
"""
import logging
import sys
from functools import wraps
from typing import Any, Callable, Optional
import traceback

def setup_logging(level: str = 'INFO', log_file: str = 'pdf_fetcher.log') -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Log file path
        
    Returns:
        logging.Logger: Configured logger
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    return root_logger

def handle_exceptions(logger: Optional[logging.Logger] = None, 
                     reraise: bool = True, 
                     default_return: Any = None):
    """
    Decorator for handling exceptions with logging
    
    Args:
        logger: Logger instance (if None, uses module logger)
        reraise: Whether to reraise the exception
        default_return: Value to return if exception occurs and reraise is False
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log = logger or logging.getLogger(func.__module__)
                log.error(f"Error in {func.__name__}: {e}")
                log.debug(f"Traceback: {traceback.format_exc()}")
                
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator

class GmailPDFFetcherError(Exception):
    """Base exception for Gmail PDF Fetcher"""
    pass

class AuthenticationError(GmailPDFFetcherError):
    """Authentication related errors"""
    pass

class EmailSearchError(GmailPDFFetcherError):
    """Email search related errors"""
    pass

class DownloadError(GmailPDFFetcherError):
    """Download related errors"""
    pass

class ConfigurationError(GmailPDFFetcherError):
    """Configuration related errors"""
    pass

def validate_date_range(start_date: str, end_date: str) -> tuple:
    """
    Validate and parse date range
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        tuple: (start_datetime, end_datetime)
        
    Raises:
        ValueError: If dates are invalid
    """
    try:
        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt >= end_dt:
            raise ValueError("Start date must be before end date")
        
        return start_dt, end_dt
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. {e}")

def validate_credentials_file(credentials_file: str) -> bool:
    """
    Validate credentials file exists and is readable
    
    Args:
        credentials_file (str): Path to credentials file
        
    Returns:
        bool: True if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
    """
    import os
    
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
    
    if not os.access(credentials_file, os.R_OK):
        raise PermissionError(f"Cannot read credentials file: {credentials_file}")
    
    return True

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename
    """
    import re
    
    # Remove or replace invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = 'unnamed_file'
    
    return safe_name

