def build_share_link(server_url, file_id, key_b64, hash_str):
    """Key + hash live in the URL #fragment. Browsers never transmit the
    fragment to the server, so a curl/requests client must split it off
    locally — the server never sees the key. (See security notes: the key
    is still exposed to anyone who can read the link itself.)"""
    return f"{server_url}/download/{file_id}#{key_b64}:{hash_str}"


def parse_share_link(link):
    base, fragment = link.split('#', 1)
    file_id = base.rstrip('/').split('/')[-1]
    key_b64, hash_str = fragment.split(':', 1)
    return file_id, key_b64, hash_str
