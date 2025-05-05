"""
Utility module for configuring cache performance and memory limits.

This module provides functions to set and manage cache and memory configurations
for improved system performance.
"""

import psutil
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def configure_memory_limits(max_memory_percent: float = 80.0) -> bool:
    """
    Configure memory usage limits for the current process.

    Args:
        max_memory_percent (float, optional): Maximum percentage of total system 
            memory that the process can use. Defaults to 80.0.

    Returns:
        bool: True if memory limits were successfully configured, False otherwise.
    """
    try:
        # Get total system memory
        total_memory = psutil.virtual_memory().total
        max_memory_bytes = int(total_memory * (max_memory_percent / 100.0))

        # Set memory limit using resource module
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))

        logger.info(f"Memory limit set to {max_memory_percent}% of total system memory")
        return True
    except Exception as e:
        logger.error(f"Failed to set memory limits: {e}")
        return False

def configure_cache_performance(cache_size_mb: int = 256, 
                                cache_dir: str = None) -> dict:
    """
    Configure cache performance settings.

    Args:
        cache_size_mb (int, optional): Size of cache in megabytes. Defaults to 256.
        cache_dir (str, optional): Directory to use for caching. 
                                   Defaults to system temp directory.

    Returns:
        dict: Configuration details including cache directory and size.
    """
    try:
        # Use provided cache directory or default to system temp
        if not cache_dir:
            cache_dir = os.path.join(tempfile.gettempdir(), 'prometheus_swarm_cache')

        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        # Set environment variables for cache configuration
        os.environ['PROMETHEUS_SWARM_CACHE_DIR'] = cache_dir
        os.environ['PROMETHEUS_SWARM_CACHE_SIZE_MB'] = str(cache_size_mb)

        config = {
            'cache_dir': cache_dir,
            'cache_size_mb': cache_size_mb
        }

        logger.info(f"Cache performance configured: {config}")
        return config
    except Exception as e:
        logger.error(f"Failed to configure cache performance: {e}")
        return {}

def get_current_memory_usage() -> float:
    """
    Get current process memory usage percentage.

    Returns:
        float: Current memory usage percentage.
    """
    try:
        process = psutil.Process(os.getpid())
        return process.memory_percent()
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        return -1.0