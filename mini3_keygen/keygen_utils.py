import base64

KEY_LENGTH = 32


def validate_key_length(key: bytes) -> bool:
    """AES-256 keys must be exactly 32 bytes."""
    return len(key) == KEY_LENGTH


def is_valid_base64(s: str) -> bool:
    try:
        base64.urlsafe_b64decode(s.encode())
        return True
    except (ValueError, TypeError):
        return False
