import os

NONCE_SIZE = 12


def generate_nonce():
    """A fresh 96-bit nonce. MUST be unique per (key, message)."""
    return os.urandom(NONCE_SIZE)


def read_nonce(path):
    """Pull the prepended nonce off an encrypted file without decrypting."""
    with open(path, 'rb') as f:
        return f.read(NONCE_SIZE)
