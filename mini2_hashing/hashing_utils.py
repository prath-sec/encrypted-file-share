def format_hash(hash_str, edge=4):
    """Shorten a hash for display: 'a3f9c2d1...b7e4'."""
    if len(hash_str) <= edge * 2:
        return hash_str
    return f"{hash_str[:edge]}...{hash_str[-edge:]}"

