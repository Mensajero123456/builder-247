"""
Advanced cache management with performance and memory constraints.

Implements an LRU cache with configurable max size and memory limits.
"""

import time
import logging
import functools
import psutil
import sys
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
        self._cache: Dict[str, Dict[str, Any]] = {}
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
        # Evict by age first
        now = time.time()
        current_time = now

        # Create list of keys to remove based on age
        expired_keys = [
            k for k, v in self._cache.items() 
            if current_time - v['timestamp'] > self._max_item_age
        ]
        
        # Remove items that have expired
        for key in expired_keys:
            del self._cache[key]
            self._cache_metrics['evictions'] += 1
            self._cache_metrics['current_size'] -= 1

        # If still over max items, use LRU strategy
        while len(self._cache) > self._max_items:
            # Find and remove least recently used item
            lru_key = min(self._cache, key=lambda k: self._cache[k]['timestamp'])
            del self._cache[lru_key]
            self._cache_metrics['evictions'] += 1
            self._cache_metrics['current_size'] -= 1

    def _check_memory_limit(self) -> bool:
        """Check if current memory usage is within limits."""
        process = psutil.Process()
        mem_info = process.memory_info()
        current_memory_mb = mem_info.rss / (1024 * 1024)
        
        return current_memory_mb <= self._max_memory_mb

    def set(self, key: str, value: Any) -> bool:
        """
        Set a value in the cache with performance tracking.

        Args:
            key (str): Cache key
            value (Any): Value to cache

        Returns:
            bool: Whether item was successfully cached
        """
        if not self._check_memory_limit():
            logger.warning("Memory limit exceeded. Cannot cache item.")
            return False

        # Always call eviction check before setting
        self._evict_if_needed()

        # Simple size approximation
        size_estimate = sys.getsizeof(value)
        
        if size_estimate > self._max_memory_mb * 1024 * 1024:
            logger.warning(f"Item too large to cache: {size_estimate} bytes")
            return False

        # Remove existing key to reset its access time
        if key in self._cache:
            del self._cache[key]
            self._cache_metrics['current_size'] -= 1

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

        # Update timestamp for LRU
        item = self._cache[key]
        current_time = time.time()

        # Check for item expiration
        if current_time - item['timestamp'] > self._max_item_age:
            del self._cache[key]
            self._cache_metrics['current_size'] -= 1
            self._cache_metrics['misses'] += 1
            return None

        item['timestamp'] = current_time
        
        self._cache_metrics['hits'] += 1
        return item['value']

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