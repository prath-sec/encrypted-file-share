import os
import pytest
from cryptography.exceptions import InvalidTag

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from encryptor import encrypt_file, decrypt_file
from encryption_utils import generate_nonce, read_nonce
from mini3_keygen.keygen import generate_aes_key


@pytest.fixture
def plaintext_file(tmp_path):
    p = tmp_path / "secret.txt"
    p.write_text("attack at dawn")
    return str(p)


def test_encrypt_decrypt_roundtrip(plaintext_file, tmp_path):
    key = generate_aes_key()
    enc = str(tmp_path / "out.enc")
    dec = str(tmp_path / "out.dec")
    encrypt_file(plaintext_file, enc, key)
    decrypt_file(enc, dec, key)
    with open(plaintext_file, 'rb') as a, open(dec, 'rb') as b:
        assert a.read() == b.read()


def test_wrong_key_raises(plaintext_file, tmp_path):
    enc = str(tmp_path / "out.enc")
    encrypt_file(plaintext_file, enc, generate_aes_key())
    with pytest.raises(InvalidTag):
        decrypt_file(enc, str(tmp_path / "x.dec"), generate_aes_key())


def test_same_file_twice_differs(plaintext_file, tmp_path):
    key = generate_aes_key()
    e1 = str(tmp_path / "a.enc")
    e2 = str(tmp_path / "b.enc")
    encrypt_file(plaintext_file, e1, key)
    encrypt_file(plaintext_file, e2, key)
    # Different nonces => different ciphertext, even for identical input+key.
    with open(e1, 'rb') as a, open(e2, 'rb') as b:
        assert a.read() != b.read()


def test_ciphertext_is_unreadable(plaintext_file, tmp_path):
    key = generate_aes_key()
    enc = str(tmp_path / "out.enc")
    encrypt_file(plaintext_file, enc, key)
    with open(enc, 'rb') as f:
        blob = f.read()
    assert b"attack at dawn" not in blob


def test_tampering_detected(plaintext_file, tmp_path):
    key = generate_aes_key()
    enc = str(tmp_path / "out.enc")
    encrypt_file(plaintext_file, enc, key)
    raw = bytearray(open(enc, 'rb').read())
    raw[-1] ^= 0x01  # flip one bit in the tag
    with open(enc, 'wb') as f:
        f.write(raw)
    with pytest.raises(InvalidTag):
        decrypt_file(enc, str(tmp_path / "x.dec"), key)


def test_nonce_is_12_bytes():
    assert len(generate_nonce()) == 12


def test_read_nonce_matches(plaintext_file, tmp_path):
    key = generate_aes_key()
    enc = str(tmp_path / "out.enc")
    encrypt_file(plaintext_file, enc, key)
    assert len(read_nonce(enc)) == 12
