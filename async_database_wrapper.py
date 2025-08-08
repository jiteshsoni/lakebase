#!/usr/bin/env python3
"""
Compatibility wrapper for async_database.py
This file maintains backward compatibility while the actual implementation
has been moved to src/database/async_database.py
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import all the functions from the actual module
from database.async_database import *

# Re-export all the functions for backward compatibility
__all__ = [
    'load_config',
    'init_engine', 
    'refresh_token_background',
    'start_token_refresh',
    'stop_token_refresh',
    'get_db',
    'token_required_wrapper',
    'lifespan'
]

# Add load_config function for backward compatibility
def load_config():
    """Load configuration securely from environment variables"""
    from src.core.secure_credentials import get_secure_credentials
    return get_secure_credentials()