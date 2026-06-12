import os


def generate_salt(length=16):
    """Random salt for PBKDF2. Must be stored alongside derived-key data,
    but is NOT secret — its job is to defeat precomputed rainbow tables."""
    return os.urandom(length)


def save_key(key: bytes, path: str):
    """Write raw key bytes to disk with owner-only permissions."""
    with open(path, 'wb') as f:
        f.write(key)
    # Restrict to read/write for the owner only (POSIX). No-op on Windows.
    try:
        os.chmod(path, 0o600)
    except (OSError, NotImplementedError):
        pass


def load_key(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()
