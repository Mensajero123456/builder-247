"""
Performance and monitoring tests for cache implementation.
"""

import time
import pytest
from src.utils.cache_performance import PerformanceCache, performance_cached

def test_cache_max_items():
    """Test cache respects maximum number of items."""
    cache = PerformanceCache(max_items=3)
    
    # Add 5 items
    for i in range(5):
        cache.set(str(i), i)
    
    # Check metrics
    metrics = cache.get_metrics()
    assert metrics['current_size'] <= 3
    assert metrics['evictions'] > 0

def test_cache_memory_limit():
    """Test cache respects memory limits."""
    cache = PerformanceCache(max_memory_mb=1)  # Very small memory limit
    
    # Try to cache large objects
    large_object = 'x' * (2 * 1024 * 1024)  # 2MB object
    result = cache.set('large', large_object)
    
    assert result is False, "Should not cache item exceeding memory limit"

def test_lru_eviction():
    """Test Least Recently Used (LRU) eviction strategy."""
    cache = PerformanceCache(max_items=3)
    
    # Add initial items
    cache.set('item1', 1)
    cache.set('item2', 2)
    cache.set('item3', 3)
    
    # Access item1 to make it most recently used
    cache.get('item1')
    
    # Add another item to trigger eviction
    cache.set('item4', 4)
    
    # Check that least recently used item (item2) was evicted
    assert cache.get('item2') is None
    assert cache.get('item1') is not None
    assert cache.get('item3') is not None
    assert cache.get('item4') is not None

def test_item_age_expiration():
    """Test item age-based expiration."""
    cache = PerformanceCache(max_item_age_seconds=1)
    
    cache.set('item', 42)
    assert cache.get('item') == 42
    
    # Wait for item to expire
    time.sleep(2)
    
    assert cache.get('item') is None

def test_performance_cached_decorator():
    """Test performance cached decorator."""
    call_count = 0

    @performance_cached(max_items=2)
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call computes
    result1 = expensive_function(5)
    assert result1 == 10
    assert call_count == 1

    # Second call uses cached result
    result2 = expensive_function(5)
    assert result2 == 10
    assert call_count == 1

    # Different input triggers new computation
    result3 = expensive_function(6)
    assert result3 == 12
    assert call_count == 2

def test_cache_metrics():
    """Test cache metrics tracking."""
    cache = PerformanceCache()
    
    cache.set('key1', 1)
    cache.set('key2', 2)
    cache.get('key1')
    cache.get('key2')
    cache.get('nonexistent')
    
    metrics = cache.get_metrics()
    assert metrics['hits'] == 2
    assert metrics['misses'] == 1
    assert metrics['current_size'] == 2