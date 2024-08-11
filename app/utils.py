import hashlib
import os
import logging

# Setup logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def generate_api_key():
    """
    Generate a unique API key and its hashed version.
    """
    logger.info("Generating new API key")
    api_key = os.urandom(16).hex()
    hashed_api_key = hash_api_key(api_key)
    return api_key, hashed_api_key

def hash_api_key(api_key):
    """
    Hash an API key using SHA-256.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()
