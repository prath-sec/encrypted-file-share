from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

NONCE_SIZE = 12  # 96 bits — the recommended nonce length for GCM


def encrypt_file(input_path, output_path, key):
    """Encrypt with AES-256-GCM. A fresh random nonce is generated per call
    and prepended to the output: [12-byte nonce][ciphertext+tag]."""
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    with open(input_path, 'rb') as f:
        data = f.read()
    encrypted = aesgcm.encrypt(nonce, data, None)
    with open(output_path, 'wb') as f:
        f.write(nonce + encrypted)


def decrypt_file(input_path, output_path, key):
    """Reverse encrypt_file. Raises InvalidTag if the key is wrong or the
    file was tampered with — decryption fails loudly, never silently."""
    with open(input_path, 'rb') as f:
        raw = f.read()
    nonce, ciphertext = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    aesgcm = AESGCM(key)
    data = aesgcm.decrypt(nonce, ciphertext, None)  # InvalidTag on tamper
    with open(output_path, 'wb') as f:
        f.write(data)
