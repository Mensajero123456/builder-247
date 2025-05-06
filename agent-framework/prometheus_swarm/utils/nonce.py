import secrets
import time
import hashlib

class NonceGenerator:
    """
    A service for generating secure, unique nonces.
    
    Nonces are one-time use tokens that help prevent replay attacks 
    and provide additional security for authentication and validation.
    """
    
    @staticmethod
    def generate_nonce(length=32):
        """
        Generate a cryptographically secure random nonce.
        
        Args:
            length (int, optional): Length of the nonce in bytes. Defaults to 32.
        
        Returns:
            str: A hexadecimal representation of the nonce.
        
        Raises:
            ValueError: If length is less than 8 or greater than 64.
        """
        if length < 8 or length > 64:
            raise ValueError("Nonce length must be between 8 and 64 bytes.")
        
        # Use secrets module for cryptographically strong random generation
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_timestamp_nonce(secret_key=''):
        """
        Generate a nonce that combines timestamp and optional secret key.
        
        Args:
            secret_key (str, optional): An additional secret to mix into the nonce. 
                                        Defaults to empty string.
        
        Returns:
            str: A unique nonce that includes the current timestamp and optional secret.
        """
        current_time = str(time.time())
        base_nonce = current_time + secret_key
        
        # Use SHA-256 for consistent, deterministic nonce generation
        return hashlib.sha256(base_nonce.encode()).hexdigest()
    
    @staticmethod
    def validate_nonce(nonce, max_age_seconds=3600):
        """
        Validate a timestamp-based nonce.
        
        Args:
            nonce (str): The nonce to validate.
            max_age_seconds (int, optional): Maximum allowed age of the nonce. 
                                             Defaults to 1 hour.
        
        Returns:
            bool: True if nonce is valid, False otherwise.
        
        Raises:
            TypeError: If nonce is not a string or not a valid hash.
        """
        try:
            # Validate nonce format
            if not isinstance(nonce, str) or len(nonce) != 64:
                return False
            
            # Interpret the first part of the hex hash as a timestamp
            timestamp_hex = nonce[:16]
            nonce_timestamp = int(timestamp_hex, 16)
            
            current_time = int(time.time())
            return abs(current_time - nonce_timestamp) <= max_age_seconds
        
        except (ValueError, TypeError):
            return False