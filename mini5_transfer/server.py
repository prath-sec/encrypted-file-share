from flask import Flask, request, send_file, jsonify, abort
import os
import threading
import time

import sys
sys.path.insert(0, os.path.dirname(__file__))
from transfer_utils import validate_file_id

app = Flask(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_UPLOAD_BYTES = 100 * 1024 * 1024     # 100 MB cap — refuse anything larger
FILE_TTL_SECONDS = 3600                   # blobs self-delete after 1 hour
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_BYTES


def _safe_path(file_id):
    """Resolve a validated file_id to a path INSIDE UPLOAD_DIR, or abort."""
    if not validate_file_id(file_id):
        abort(400, "Invalid file id")
    path = os.path.join(UPLOAD_DIR, file_id)
    # Defense in depth: confirm the resolved path can't escape UPLOAD_DIR.
    if os.path.commonpath([os.path.realpath(path), os.path.realpath(UPLOAD_DIR)]) != os.path.realpath(UPLOAD_DIR):
        abort(400, "Invalid path")
    return path


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    f = request.files['file']
    import uuid
    file_id = str(uuid.uuid4())
    f.save(os.path.join(UPLOAD_DIR, file_id))
    return jsonify({"file_id": file_id}), 200


@app.route('/download/<file_id>')
def download(file_id):
    path = _safe_path(file_id)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    return send_file(path, as_attachment=True, download_name=file_id)


def _reaper():
    """Background thread: delete blobs older than FILE_TTL_SECONDS."""
    while True:
        now = time.time()
        for name in os.listdir(UPLOAD_DIR):
            p = os.path.join(UPLOAD_DIR, name)
            try:
                if now - os.path.getmtime(p) > FILE_TTL_SECONDS:
                    os.remove(p)
            except OSError:
                pass
        time.sleep(60)


if __name__ == '__main__':
    threading.Thread(target=_reaper, daemon=True).start()
    app.run(port=5000)
