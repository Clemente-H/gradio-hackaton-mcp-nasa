# src/utils.py
"""Utility functions for NASA Space Explorer."""

import time
import logging
from functools import wraps
from typing import Any, Callable

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def rate_limit(min_interval: float = 3.6):
    """Decorator for rate limiting function calls."""
    last_called = [0]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last = current_time - last_called[0]
            
            if time_since_last < min_interval:
                time.sleep(min_interval - time_since_last)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator