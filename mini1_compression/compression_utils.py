import os

# Formats whose bytes are already compressed — gzip would waste CPU and
# can even make them slightly larger.
ALREADY_COMPRESSED = {
    '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi',
    '.zip', '.gz', '.7z', '.rar', '.mp3', '.webp', '.pdf',
}


def get_file_size(path):
    """Size in bytes."""
    return os.path.getsize(path)


def should_compress(path):
    """Return False for formats that are already compressed."""
    ext = os.path.splitext(path)[1].lower()
    return ext not in ALREADY_COMPRESSED
