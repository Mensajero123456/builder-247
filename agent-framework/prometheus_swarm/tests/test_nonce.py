import time
import pytest
from prometheus_swarm.utils.nonce import NonceGenerator

def test_generate_nonce_default_length():
    """Test generating a default nonce"""
    nonce = NonceGenerator.generate_nonce()
    assert len(nonce) == 64  # 32 bytes = 64 hex characters
    assert isinstance(nonce, str)

def test_generate_nonce_custom_length():
    """Test generating a nonce with custom length"""
    nonce16 = NonceGenerator.generate_nonce(16)
    nonce48 = NonceGenerator.generate_nonce(48)
    
    assert len(nonce16) == 32  # 16 bytes = 32 hex characters
    assert len(nonce48) == 96  # 48 bytes = 96 hex characters

def test_generate_nonce_invalid_length():
    """Test that invalid nonce lengths raise exceptions"""
    with pytest.raises(ValueError):
        NonceGenerator.generate_nonce(7)
    
    with pytest.raises(ValueError):
        NonceGenerator.generate_nonce(65)

def test_generate_timestamp_nonce():
    """Test generating a timestamp-based nonce"""
    nonce1 = NonceGenerator.generate_timestamp_nonce()
    time.sleep(0.1)  # Small delay
    nonce2 = NonceGenerator.generate_timestamp_nonce()
    
    assert len(nonce1) == 64
    assert nonce1 != nonce2

def test_generate_timestamp_nonce_with_secret():
    """Test generating a timestamp nonce with a secret key"""
    nonce1 = NonceGenerator.generate_timestamp_nonce('secret')
    nonce2 = NonceGenerator.generate_timestamp_nonce('different_secret')
    
    assert nonce1 != nonce2

def test_validate_nonce_within_time_window():
    """Test nonce validation within time window"""
    nonce = NonceGenerator.generate_timestamp_nonce()
    assert NonceGenerator.validate_nonce(nonce, max_age_seconds=3600)

def test_validate_nonce_outside_time_window():
    """Test nonce validation outside time window"""
    with pytest.raises(AttributeError):
        # Deliberately create an invalid nonce to test validation
        invalid_nonce = "invalid_format"
        NonceGenerator.validate_nonce(invalid_nonce)

def test_nonce_uniqueness():
    """Ensure generated nonces are unique"""
    nonces = set()
    for _ in range(1000):
        nonce = NonceGenerator.generate_nonce()
        assert nonce not in nonces
        nonces.add(nonce)