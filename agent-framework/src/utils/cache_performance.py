"""
Advanced cache management with performance and memory constraints.

Implements an LRU cache with configurable max size and memory limits.
"""

import time
import logging
import functools
import psutil
import sys
import collections
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class PerformanceCache:
    def __init__(
        self, 
        max_items: int = 100, 
        max_memory_mb: int = 50, 
        max_item_age_seconds: int = 3600
    ):
        """
        Initialize a performance-aware LRU cache.

        Args:
            max_items (int): Maximum number of items in cache
            max_memory_mb (int): Maximum memory usage in megabytes
            max_item_age_seconds (int): Maximum time an item can stay in cache
        """
        self._cache = collections.OrderedDict()
        self._max_items = max_items
        self._max_memory_mb = max_memory_mb
        self._max_item_age = max_item_age_seconds
        self._cache_metrics = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'current_size': 0
        }

    def _evict_if_needed(self) -> None:
        """Evict items if cache exceeds size or memory limits."""
        now = time.time()

        # Remove expired items first
        for key in list(self._cache.keys()):
            if now - self._cache[key]['timestamp'] > self._max_item_age:
                del self._cache[key]
                self._cache_metrics['evictions'] += 1
                self._cache_metrics['current_size'] -= 1

        # Remove least recently used items beyond max_items
        while len(self._cache) > self._max_items:
            self._cache.popitem(last=False)
            self._cache_metrics['evictions'] += 1
            self._cache_metrics['current_size'] -= 1

    def _check_memory_limit(self, size_estimate: int) -> bool:
        """Check if current memory usage is within limits."""
        process = psutil.Process()
        mem_info = process.memory_info()
        current_memory_mb = mem_info.rss / (1024 * 1024)
        
        return (current_memory_mb + size_estimate / (1024 * 1024)) <= self._max_memory_mb

    def set(self, key: str, value: Any) -> bool:
        """
        Set a value in the cache with performance tracking.

        Args:
            key (str): Cache key
            value (Any): Value to cache

        Returns:
            bool: Whether item was successfully cached
        """
        # Remove existing key to reset its order
        if key in self._cache:
            del self._cache[key]
            self._cache_metrics['current_size'] -= 1

        # Simple size approximation
        size_estimate = sys.getsizeof(value)
        
        if not self._check_memory_limit(size_estimate):
            logger.warning("Memory limit exceeded. Cannot cache item.")
            return False

        if size_estimate > self._max_memory_mb * 1024 * 1024:
            logger.warning(f"Item too large to cache: {size_estimate} bytes")
            return False

        # Always call eviction before adding new item
        self._evict_if_needed()

        # Add to end of OrderedDict (most recently used)
        self._cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        self._cache_metrics['current_size'] += 1

        return True

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Args:
            key (str): Cache key

        Returns:
            Value if found, None otherwise
        """
        if key not in self._cache:
            self._cache_metrics['misses'] += 1
            return None

        # Check for item age
        current_time = time.time()
        if current_time - self._cache[key]['timestamp'] > self._max_item_age:
            del self._cache[key]
            self._cache_metrics['current_size'] -= 1
            self._cache_metrics['misses'] += 1
            return None

        # Move to end (most recently used)
        value = self._cache[key]['value']
        del self._cache[key]
        self._cache[key] = {
            'value': value,
            'timestamp': current_time
        }
        
        self._cache_metrics['hits'] += 1
        return value

    def get_metrics(self) -> Dict[str, int]:
        """
        Get cache performance metrics.

        Returns:
            Dict of cache metrics
        """
        return self._cache_metrics.copy()

def performance_cached(
    max_items: int = 100, 
    max_memory_mb: int = 50
):
    """
    Decorator for caching function results with performance constraints.

    Args:
        max_items (int): Maximum cache items
        max_memory_mb (int): Maximum memory usage
    """
    cache = PerformanceCache(max_items, max_memory_mb)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key
            key = str(args) + str(kwargs)
            
            # Try to get from cache first
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result

            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result)
            
            return result
        
        wrapper.cache_metrics = cache.get_metrics
        return wrapper
    
    return decorator