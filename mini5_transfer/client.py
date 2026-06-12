import requests


def upload_file(filepath, server_url):
    """POST a file to the server, return its file_id."""
    with open(filepath, 'rb') as f:
        resp = requests.post(f"{server_url}/upload", files={'file': f})
    resp.raise_for_status()
    return resp.json()['file_id']


def download_file(file_id, server_url, save_path):
    """GET a file by id and stream it to disk."""
    with requests.get(f"{server_url}/download/{file_id}", stream=True) as resp:
        resp.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    return save_path
