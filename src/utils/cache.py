"""
Caching utilities for Linear API data
"""

import streamlit as st
from typing import Callable, Any, Optional, List, Dict
from functools import wraps
from config.settings import CACHE_TTL


def cached_api_call(ttl: Optional[int] = None):
    """
    Decorator for caching API calls using Streamlit's cache

    Args:
        ttl: Time to live in seconds (uses CACHE_TTL from config if not provided)

    Returns:
        Decorated function
    """
    cache_ttl = ttl or CACHE_TTL

    def decorator(func: Callable) -> Callable:
        # Use st.cache_data for data that doesn't contain unhashable types
        cached_func = st.cache_data(ttl=cache_ttl, show_spinner=False)(func)
        return cached_func

    return decorator


def clear_cache():
    """Clear all Streamlit caches"""
    st.cache_data.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics

    Returns:
        dict: Cache statistics
    """
    # Streamlit doesn't provide direct cache stats, so this is a placeholder
    return {
        "ttl": CACHE_TTL,
        "status": "enabled"
    }
