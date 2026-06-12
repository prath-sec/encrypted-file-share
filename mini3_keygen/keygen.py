import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Match the file-share guide's parameters.
PBKDF2_ITERATIONS = 480_000
KEY_LENGTH = 32  # 256 bits for AES-256


def generate_aes_key():
    """A fresh 256-bit key from the OS CSPRNG. Unique per file."""
    return os.urandom(KEY_LENGTH)


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Turn a human password into a 256-bit key via PBKDF2-HMAC-SHA256.
    Same password + same salt always yields the same key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode())


def key_to_base64(key: bytes) -> str:
    """URL-safe base64 so the key can live in a share link."""
    return base64.urlsafe_b64encode(key).decode()


def base64_to_key(s: str) -> bytes:
    return base64.urlsafe_b64decode(s.encode())


if __name__ == "__main__":
    key = generate_aes_key()
    print(f"Random AES-256 key (base64): {key_to_base64(key)}")
