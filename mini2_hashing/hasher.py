import hashlib


def generate_hash(filepath):
    """SHA-256 of a file, read in chunks so large files stay memory-safe."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_hash(filepath, expected_hash):
    """Re-hash a file and compare against the expected value."""
    actual = generate_hash(filepath)
    if actual == expected_hash:
        print("SUCCESS: File is intact and untampered.")
        return True
    print("WARNING: File has been modified or corrupted!")
    print(f"  Expected: {expected_hash}")
    print(f"  Got:      {actual}")
    return False


if __name__ == "__main__":
    path = input("File to hash: ").strip()
    h = generate_hash(path)
    print(f"SHA-256: {h}")
    check = input("Paste a hash to verify (Enter to skip): ").strip()
    if check:
        verify_hash(path, check)
