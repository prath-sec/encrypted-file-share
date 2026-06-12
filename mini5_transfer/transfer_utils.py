import re

# A file_id must be a canonical UUID4 string — nothing else touches the disk.
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


def validate_file_id(file_id: str) -> bool:
    """True only for a well-formed UUID4. Blocks path traversal like
    '../../etc/passwd' from ever reaching the filesystem."""
    return bool(_UUID_RE.match(file_id))


def format_link(link: str) -> str:
    """Trim stray whitespace a user might paste in."""
    return link.strip()
