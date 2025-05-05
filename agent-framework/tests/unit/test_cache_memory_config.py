"""
Unit tests for cache and memory configuration utility.
"""

import os
import pytest
import tempfile
from prometheus_swarm.utils.cache_memory_config import (
    configure_memory_limits,
    configure_cache_performance,
    get_current_memory_usage
)

def test_configure_memory_limits():
    """Test memory limits configuration."""
    # Test default configuration
    result = configure_memory_limits()
    assert result is True, "Memory limits configuration should succeed"

    # Test with custom percentage
    result = configure_memory_limits(max_memory_percent=50.0)
    assert result is True, "Custom memory limits configuration should succeed"

def test_configure_cache_performance():
    """Test cache performance configuration."""
    # Test default configuration
    config = configure_cache_performance()
    assert config is not None, "Cache configuration should return a config dict"
    assert 'cache_dir' in config, "Config should include cache directory"
    assert 'cache_size_mb' in config, "Config should include cache size"
    assert os.path.exists(config['cache_dir']), "Cache directory should be created"

    # Test with custom parameters
    custom_dir = os.path.join(tempfile.gettempdir(), 'custom_cache')
    config = configure_cache_performance(cache_size_mb=512, cache_dir=custom_dir)
    assert config['cache_dir'] == custom_dir, "Should use provided cache directory"
    assert config['cache_size_mb'] == 512, "Should use provided cache size"

def test_get_current_memory_usage():
    """Test getting current memory usage."""
    memory_usage = get_current_memory_usage()
    assert isinstance(memory_usage, float), "Memory usage should be a float"
    assert memory_usage >= 0, "Memory usage percentage should be non-negative"