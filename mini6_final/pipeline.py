import os
import sys

# Put every mini package on the path (conftest does this for tests; we do it
# here so the CLI works when run directly).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for d in ["mini1_compression", "mini2_hashing", "mini3_keygen",
          "mini4_encryption", "mini5_transfer", "mini6_final"]:
    sys.path.insert(0, os.path.join(ROOT, d))

from compressor import compress_file
from compression_utils import should_compress
from hasher import generate_hash, verify_hash
from keygen import generate_aes_key, key_to_base64, base64_to_key
from encryptor import encrypt_file, decrypt_file
from client import upload_file, download_file
from link_generator import build_share_link, parse_share_link
from safe_decompress import bounded_decompress

SERVER = os.environ.get("SHARE_SERVER", "http://localhost:5000")

def send_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No such file: {filepath}")

    print("[1/5] Hashing original file...")
    file_hash = generate_hash(filepath)

    print("[2/5] Compressing...")
    gz_path = filepath + ".gz"
    compressed = False
    if should_compress(filepath):
        compress_file(filepath, gz_path)
        compressed = True
    else:
        gz_path = filepath
        print("      Skipped (already-compressed format).")

    print("[3/5] Generating encryption key...")
    key = generate_aes_key()

    print("[4/5] Encrypting...")
    enc_path = filepath + ".enc"
    encrypt_file(gz_path, enc_path, key)

    print("[5/5] Uploading...")
    file_id = upload_file(enc_path, SERVER)

    # The receiver needs to know whether to decompress. Pack a flag into the
    # hash field so the link format stays the same: "<hash>|<c|p>".
    marker = "c" if compressed else "p"
    link = build_share_link(SERVER, file_id, key_to_base64(key),
                            f"{file_hash}|{marker}")

    # Clean up local scratch files.
    for p in (enc_path, gz_path if compressed else None):
        if p and os.path.exists(p):
            os.remove(p)

    print("\nDone! Share this link:")
    print(f"  {link}")
    return link


def receive_file(link, save_path):
    file_id, key_b64, hash_field = parse_share_link(link.strip())
    expected_hash, marker = hash_field.split("|", 1)
    key = base64_to_key(key_b64)

    print("[1/4] Downloading...")
    enc_path = "temp_download.enc"
    download_file(file_id, SERVER, enc_path)

    print("[2/4] Decrypting...")
    gz_path = "temp_download.gz"
    decrypt_file(enc_path, gz_path, key)   # raises InvalidTag if tampered

    print("[3/4] Decompressing...")
    if marker == "c":
        bounded_decompress(gz_path, save_path)
    else:
        # Was never compressed — the decrypted bytes are the file.
        os.replace(gz_path, save_path)
        gz_path = None

    print("[4/4] Verifying integrity...")
    ok = verify_hash(save_path, expected_hash)

    # Clean up temp files.
    for p in (enc_path, gz_path):
        if p and os.path.exists(p):
            os.remove(p)

    if ok:
        print(f"\nFile saved as: {save_path}")
    else:
        print("\nWARNING: Integrity check failed — file may be corrupt!")
    return ok
