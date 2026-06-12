import pytest
from keygen import (
    generate_aes_key, derive_key_from_password,
    key_to_base64, base64_to_key,
)
from key_store import save_key, load_key, generate_salt
from keygen_utils import validate_key_length, is_valid_base64


def test_key_is_32_bytes():
    assert len(generate_aes_key()) == 32


def test_keys_are_unique():
    assert generate_aes_key() != generate_aes_key()


def test_pbkdf2_deterministic():
    salt = b"fixed_salt_16byte"
    k1 = derive_key_from_password("hunter2", salt)
    k2 = derive_key_from_password("hunter2", salt)
    assert k1 == k2


def test_pbkdf2_different_salt_different_key():
    k1 = derive_key_from_password("hunter2", generate_salt())
    k2 = derive_key_from_password("hunter2", generate_salt())
    assert k1 != k2


def test_base64_roundtrip():
    key = generate_aes_key()
    assert base64_to_key(key_to_base64(key)) == key


def test_save_and_load(tmp_path):
    key = generate_aes_key()
    path = str(tmp_path / "test.key")
    save_key(key, path)
    assert load_key(path) == key


def test_validate_key_length():
    assert validate_key_length(generate_aes_key()) is True
    assert validate_key_length(b"too short") is False


def test_is_valid_base64():
    assert is_valid_base64(key_to_base64(generate_aes_key())) is True


def test_salt_is_random():
    assert generate_salt() != generate_salt()
