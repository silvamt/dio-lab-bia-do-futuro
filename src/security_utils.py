"""
Security utilities for input validation and sanitization.
Provides functions to validate and sanitize user input to prevent injection attacks.
"""

import re
import os
from typing import Optional
import logging

from constants import MAX_QUERY_LENGTH

logger = logging.getLogger(__name__)


def sanitize_user_input(user_input: str, max_length: int = MAX_QUERY_LENGTH) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input string
        
    Raises:
        ValueError: If input is invalid or too long
    """
    if not user_input or not isinstance(user_input, str):
        raise ValueError("Input must be a non-empty string")
    
    # Strip whitespace
    sanitized = user_input.strip()
    
    # Check length
    if len(sanitized) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    # Remove any control characters except common whitespace
    sanitized = ''.join(char for char in sanitized if char.isprintable() or char in '\n\t ')
    
    # Additional check for empty after sanitization
    if not sanitized:
        raise ValueError("Input is empty after sanitization")
    
    return sanitized


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate API key format without exposing the key.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if key appears valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation: key should have reasonable length and no whitespace
    if len(api_key.strip()) < 10 or len(api_key.strip()) > 500:
        return False
    
    if ' ' in api_key or '\n' in api_key or '\t' in api_key:
        return False
    
    return True


def get_secure_env_var(var_name: str) -> Optional[str]:
    """
    Safely retrieve environment variable with validation.
    
    Args:
        var_name: Name of environment variable
        
    Returns:
        Environment variable value if valid, None otherwise
    """
    try:
        value = os.getenv(var_name)
        if value and validate_api_key(value):
            return value
        return None
    except Exception as e:
        logger.error(f"Error retrieving environment variable {var_name}: {e}")
        return None


def validate_file_path(file_path: str, base_dir: str) -> bool:
    """
    Validate that file path is safe (no directory traversal).
    
    Args:
        file_path: Path to validate
        base_dir: Base directory that should contain the file
        
    Returns:
        True if path is safe, False otherwise
    """
    try:
        from pathlib import Path
        
        # Resolve both paths to absolute
        base = Path(base_dir).resolve()
        target = Path(file_path).resolve()
        
        # Check if target is within base directory
        return str(target).startswith(str(base))
    except Exception as e:
        logger.error(f"Error validating file path: {e}")
        return False
